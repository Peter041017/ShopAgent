from src.agent.state import AgentState
from src.tools import DANGEROUS_TOOLS
from src.tools.logistics_tools import track_logistics
from src.tools.order_tools import list_user_orders, query_order
from src.tools.product_tools import search_products
from src.tools.refund_tools import query_refund_policy, submit_refund


async def tool_executor_node(state: AgentState) -> dict:
    intent = state.get("intent", "unknown")
    slots = state.get("slots") or {}
    user_id = state.get("user_id") or "guest"
    tool_results: list[dict] = []
    last = state["messages"][-1]
    user_text = str(last.content if hasattr(last, "content") else last)

    # 多轮对话：检查上下文中是否有历史槽位值可继承
    history = state.get("conversation_history") or ""

    # 如果在历史中提到过订单号但当前槽位为空，尝试从历史提取
    if not slots.get("order_id") and history:
        for line in history.split("\n"):
            if "订单号" in line or "ORD-" in line:
                import re
                m = re.search(r"(ORD[-\w]+)", line)
                if m:
                    slots["order_id"] = m.group(1)
                    break

    # ── 物流查询：单独检测 tracking_number ──────────────
    if slots.get("tracking_number"):
        tracking_no = str(slots["tracking_number"])
        out = await track_logistics.ainvoke({"tracking_number": tracking_no})
        tool_results.append({"name": "track_logistics", "content": out})
        return {"tool_results": tool_results, "needs_clarification": False}

    # ── 商品搜索 ─────────────────────────────────────
    if intent == "product_inquiry" or slots.get("product_name") or slots.get("keyword"):
        keyword = str(slots.get("product_name") or slots.get("keyword") or "")
        if keyword:
            out = await search_products.ainvoke({
                "keyword": keyword,
                "category": slots.get("category", ""),
                "price_min": 0,
                "price_max": 999999,
            })
            tool_results.append({"name": "search_products", "content": out})
            return {"tool_results": tool_results, "needs_clarification": False}

    # ── 订单查询 ─────────────────────────────────────
    if intent == "order_query":
        order_id = slots.get("order_id")

        if not order_id or order_id == "LIST":
            out = await list_user_orders.ainvoke(
                {"user_id": str(user_id), "status_filter": slots.get("status_filter", "all")}
            )
            tool_results.append({"name": "list_user_orders", "content": out})
            return {"tool_results": tool_results, "needs_clarification": False}

        out = await query_order.ainvoke({"order_id": str(order_id), "user_id": str(user_id)})
        tool_results.append({"name": "query_order", "content": out})
        return {"tool_results": tool_results, "needs_clarification": False}

    # ── 售后服务 ─────────────────────────────────────
    if intent == "after_sales":
        issue_type = str(slots.get("issue_type") or "").lower()
        order_id = slots.get("order_id")

        # 判断是「咨询政策」还是「申请操作」
        policy_keywords = ("条件", "政策", "规则", "可以退吗", "怎么退", "多久", "流程")
        is_policy_query = any(k in user_text for k in policy_keywords)

        # 判断是否明确要求执行退款操作
        action_keywords = ("我要退款", "申请退款", "帮我退", "提交退款", "refund", "return")
        is_refund_action = any(k in user_text for k in action_keywords) or any(
            k in issue_type for k in ("退款", "退货", "退钱")
        )

        if is_refund_action and not is_policy_query:
            if order_id:
                if submit_refund.name in DANGEROUS_TOOLS:
                    out = await submit_refund.ainvoke(
                        {"order_id": str(order_id), "reason": "用户申请退款"}
                    )
                    tool_results.append({"name": submit_refund.name, "content": out})
                    return {
                        "tool_results": tool_results,
                        "needs_clarification": False,
                        "needs_human": True,
                    }
            # 有退款意图但无订单号 → 问订单号
            return {
                "needs_clarification": True,
                "clarification_question": "请提供需要退款的订单号。",
                "tool_results": [],
            }

        # 默认：查询退款政策（涵盖政策咨询、信息查询）
        out = await query_refund_policy.ainvoke({"product_category": slots.get("category", "general")})
        tool_results.append({"name": "query_refund_policy", "content": out})
        return {"tool_results": tool_results, "needs_clarification": False}

    # ── 默认兜底 ─────────────────────────────────────
    out = await list_user_orders.ainvoke({"user_id": str(user_id), "status_filter": "all"})
    tool_results.append({"name": "list_user_orders", "content": out})
    return {"tool_results": tool_results, "needs_clarification": False}
