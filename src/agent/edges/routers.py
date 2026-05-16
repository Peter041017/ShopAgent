from src.agent.state import AgentState


def route_after_security(state: AgentState) -> str:
    """安全审核后的路由：拦截内容直接返回，通过则进入意图识别。"""
    if state.get("final_response"):
        return "rejected"
    return "passed"


def route_after_intent(state: AgentState) -> str:
    """根据意图决定下一个节点"""
    if state.get("needs_clarification"):
        return "clarify"
    intent = state.get("intent", "unknown")
    slots = state.get("slots") or {}

    if intent in ("product_inquiry",):
        # 有搜索关键词走 tool（search_products），否则走 RAG 知识库
        if slots.get("product_name") or slots.get("keyword"):
            return "tool"
        return "rag"
    if intent in ("order_query", "after_sales"):
        return "tool"
    return "respond"


def route_after_tool(state: AgentState) -> str:
    """工具执行后的路由"""
    if state.get("needs_clarification"):
        return "clarify"
    return "respond"
