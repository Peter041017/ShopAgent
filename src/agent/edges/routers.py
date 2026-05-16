from src.agent.state import AgentState


def route_after_security(state: AgentState) -> str:
    """安全审核后的路由：拦截内容直接返回，通过则进入意图识别。"""
    if state.get("_security_blocked", False):
        return "rejected"
    return "passed"


def route_after_intent(state: AgentState) -> str:
    """根据意图决定下一个节点"""
    if state.get("needs_clarification"):
        return "clarify"
    intent = state.get("intent", "unknown")
    slots = state.get("slots") or {}

    if intent in ("product_inquiry", "after_sales", "unknown"):
        # 商品知识 / 售后政策 / 未知意图都走 RAG 知识库（让 KB 兜底）
        return "rag"
    if intent in ("order_query",):
        return "tool"
    return "respond"


def route_after_rag(state: AgentState) -> str:
    """RAG 检索后的路由：after_sales 还需走 tool（退换货操作），其余直接生成回复。"""
    intent = state.get("intent", "unknown")
    if intent in ("after_sales",):
        return "tool"  # 还需要执行具体的退换货/退款操作
    return "respond"


def route_after_tool(state: AgentState) -> str:
    """工具执行后的路由"""
    if state.get("needs_clarification"):
        return "clarify"
    return "respond"
