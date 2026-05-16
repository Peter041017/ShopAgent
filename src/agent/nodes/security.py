"""安全审核节点 — 在意图识别前拦截违规内容。"""

from src.agent.state import AgentState
from src.utils.logger import get_logger
from src.utils.security import screen_user_text

logger = get_logger(__name__)


async def security_node(state: AgentState) -> dict:
    """对用户最新消息进行安全检查。

    注意：该节点必须始终显式设置 _security_blocked 字段，
    因为 LangGraph 的 MemorySaver 会恢复此前轮的 state，
    若不覆盖，条件边 route_after_security 会用旧值判断路由。
    """
    last = state["messages"][-1]
    user_message = str(last.content if hasattr(last, "content") else last)

    ok, reason = screen_user_text(user_message)
    if not ok:
        logger.warning("security_node blocked: user=%s reason=%s", state.get("user_id"), reason)
        return {
            "_security_blocked": True,
            "needs_human": False,
            "needs_clarification": False,
            "final_response": f"抱歉，您的消息未能通过安全审核（{reason}）。请调整后重试。",
            "intent": "unknown",
        }
    # 必须显式设为 False 以覆盖前轮的缓存值
    return {"_security_blocked": False}
