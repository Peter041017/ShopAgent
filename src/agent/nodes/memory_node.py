"""对话记忆节点 — 加载并格式化对话上下文。"""

from src.agent.state import AgentState
from src.memory.buffer import ConversationMemory
from src.utils.logger import get_logger

logger = get_logger(__name__)

# 全局记忆实例（生产环境可替换为 Redis 持久化版本）
_memory = ConversationMemory(max_turns=10)


async def memory_context_node(state: AgentState) -> dict:
    """加载会话历史，格式化后注入 state 供后续节点使用。"""
    session_id = state.get("session_id") or "default"

    # 获取历史消息（不含当前最新一条）
    history = _memory.get_messages(session_id)
    history_text = _memory.get_context_window(session_id, max_tokens=2000)

    if history_text:
        logger.debug("memory_context: loaded %d chars for session %s", len(history_text), session_id)
    else:
        logger.debug("memory_context: no history for session %s", session_id)

    return {"conversation_history": history_text}
