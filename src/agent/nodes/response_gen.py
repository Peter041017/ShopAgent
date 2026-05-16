from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

from src.agent.state import AgentState
from src.config.settings import settings
from src.memory.buffer import ConversationMemory
from src.utils.prompts import RAG_SYSTEM_PROMPT

_memory = ConversationMemory(max_turns=10)


async def response_generation_node(state: AgentState) -> dict:
    last = state["messages"][-1]
    user_message = last.content if hasattr(last, "content") else str(last)

    if not settings.OPENAI_API_KEY:
        docs = state.get("retrieved_docs") or []
        tools = state.get("tool_results") or []
        if tools:
            reply = str(tools[0].get("content", "（无工具结果）"))
        elif docs:
            reply = str(docs[0].get("page_content", ""))[:2000]
        else:
            reply = f"（未配置 LLM）收到：{user_message}"

        # 无 LLM 也保存记忆
        from langchain_core.messages import AIMessage
        session_id = state.get("session_id") or "default"
        _memory.add_message(session_id, HumanMessage(content=user_message))
        _memory.add_message(session_id, AIMessage(content=reply))
        return {"final_response": reply}

    llm = ChatOpenAI(
        model=settings.LLM_MODEL,
        temperature=settings.LLM_MODEL_TEMPERATURE,
        api_key=settings.OPENAI_API_KEY,
        base_url=settings.OPENAI_BASE_URL,
    )

    ctx_parts: list[str] = []
    for d in state.get("retrieved_docs") or []:
        if isinstance(d, dict):
            ctx_parts.append(d.get("page_content", ""))
    rag_block = "\n---\n".join(ctx_parts) if ctx_parts else "（无相关知识片段）"

    tool_lines: list[str] = []
    for t in state.get("tool_results") or []:
        tool_lines.append(f"[{t.get('name')}] {t.get('content')}")
    tool_block = "\n".join(tool_lines) if tool_lines else "（无工具结果）"

    history = state.get("conversation_history") or ""
    extra = ""
    if state.get("needs_human"):
        extra = "\n请在结尾提示用户：该问题已转人工处理，请留意站内信或短信。"

    prompt = (
        f"{RAG_SYSTEM_PROMPT}\n\n"
        + (f"对话历史：\n{history}\n\n" if history else "")
        + f"用户问题：{user_message}\n\n"
        + f"知识片段：\n{rag_block}\n\n"
        + f"工具结果：\n{tool_block}\n"
        + f"{extra}"
    )

    response = await llm.ainvoke(
        [
            SystemMessage(content="你是专业电商客服助手。"),
            HumanMessage(content=prompt),
        ]
    )
    reply = str(response.content).strip()

    # 保存本轮对话到记忆缓冲
    session_id = state.get("session_id") or "default"
    _memory.add_message(session_id, HumanMessage(content=user_message))
    _memory.add_message(session_id, response)

    return {"final_response": reply}
