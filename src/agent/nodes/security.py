"""安全审核节点 — 在意图识别前拦截违规内容。"""

from src.agent.state import AgentState
from src.utils.logger import get_logger
from src.utils.security import screen_user_text

logger = get_logger(__name__)


async def security_node(state: AgentState) -> dict:
    """对用户最新消息进行安全检查。"""
    last = state["messages"][-1]
    user_message = str(last.content if hasattr(last, "content") else last)

    ok, reason = screen_user_text(user_message)
    if not ok:
        logger.warning("security_node blocked: user=%s reason=%s", state.get("user_id"), reason)
        return {
            "needs_human": False,
            "needs_clarification": False,
            "final_response": f"抱歉，您的消息未能通过安全审核（{reason}）。请调整后重试。",
            "intent": "unknown",
        }
    return {}
