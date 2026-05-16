import json
import re

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

from src.agent.state import AgentState
from src.config.settings import settings
from src.utils.prompts import INTENT_SYSTEM_PROMPT


def _parse_intent_json(text: str) -> dict:
    text = text.strip()
    m = re.search(r"\{[\s\S]*\}", text)
    if m:
        text = m.group(0)
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return {"intent": "unknown", "slots": {}, "needs_clarification": False}


def _extract_slots_from_text(text: str) -> dict:
    slots = {}
    # 订单号匹配
    oid_match = re.search(r"(ORD[-\w\d]+|ORD\d+|SF\d+)", text, re.I)
    if oid_match:
        slots["order_id"] = oid_match.group(1)
    # 物流单号匹配（SF / YT / 数字开头）
    track_match = re.search(r"(SF\d{8,12}|YT\d{8,12}|\d{12,15})", text)
    if track_match:
        slots["tracking_number"] = track_match.group(1)
    # 商品名提取（常见产品系列）
    product_keywords = [
        r"(iPhone\s*\d+\s*(?:Pro|Air)?)",
        r"(MacBook\s*(?:Pro|Air)?)",
        r"(iPad\s*(?:Air|Pro|mini)?)",
        r"(AirPods)",
        r"(Apple\s*Watch)",
        r"(降噪耳机)",
        r"(音箱|音响)",
        r"(充电器|充电线|数据线)",
        r"(SSD|固态硬盘)",
    ]
    for pat in product_keywords:
        m = re.search(pat, text, re.I)
        if m:
            slots["product_name"] = m.group(1)
            break
    # 是否为订单列表查询
    if any(k in text for k in ("列表", "哪些订单", "全部订单", "所有订单", "我的订单")):
        slots["is_list_query"] = True
    return slots


async def intent_router_node(state: AgentState) -> dict:
    """识别用户意图并提取槽位信息"""
    if not settings.OPENAI_API_KEY:
        return {
            "intent": "unknown",
            "slots": {},
            "needs_clarification": False,
            "clarification_question": "",
        }

    llm = ChatOpenAI(
        model=settings.LLM_MODEL,
        temperature=0.1,
        api_key=settings.OPENAI_API_KEY,
        base_url=settings.OPENAI_BASE_URL,
    )
    last = state["messages"][-1]
    user_message = last.content if hasattr(last, "content") else str(last)

    history = state.get("conversation_history") or ""

    # 如果有多轮对话历史，将其加入上下文辅助意图判断
    context = str(user_message)
    if history:
        context = f"对话历史：\n{history}\n\n当前消息：{user_message}"

    response = await llm.ainvoke(
        [
            SystemMessage(content=INTENT_SYSTEM_PROMPT),
            HumanMessage(content=context),
        ]
    )
    result = _parse_intent_json(str(response.content))
    intent = result.get("intent", "unknown")
    slots = result.get("slots") or {}
    needs_clarification = bool(result.get("needs_clarification", False))
    clarification_question = str(result.get("clarification_question", "") or "")

    # 合并正则提取的槽位（补充 LLM 可能遗漏的信息）
    text_slots = _extract_slots_from_text(str(user_message))
    for k, v in text_slots.items():
        if v and k not in slots or not slots.get(k):
            slots[k] = v

    # 订单查询缺少订单号时尝试追问
    if intent == "order_query" and not slots.get("order_id"):
        if slots.get("is_list_query"):
            slots["order_id"] = "LIST"
        else:
            needs_clarification = True
            clarification_question = clarification_question or "请提供需要查询的订单号，例如 ORD-20260514-001。您也可以说「我的订单列表」查看所有订单。"

    # 物流查询
    if intent == "order_query" and slots.get("tracking_number") and not slots.get("order_id"):
        pass  # 交由 tool_node 处理物流查询

    return {
        "intent": intent,
        "slots": slots,
        "needs_clarification": needs_clarification,
        "clarification_question": clarification_question,
    }
