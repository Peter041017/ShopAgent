from collections import defaultdict

from langchain_core.messages import BaseMessage, HumanMessage

from src.config.settings import settings
from src.utils.logger import get_logger

logger = get_logger(__name__)

_SESSIONS: dict[str, list[BaseMessage]] = defaultdict(list)


class ConversationMemory:
    """封装对话缓冲，只保留最近 N 轮"""

    def __init__(self, max_turns: int = 10) -> None:
        self.max_turns = max_turns

    def get_messages(self, session_id: str) -> list[BaseMessage]:
        try:
            import redis

            redis.from_url(settings.REDIS_URL, decode_responses=False)
            # 生产可在此实现 List 序列化读写
        except Exception as e:
            logger.debug("redis session read skipped: %s", e)
        return list(_SESSIONS.get(session_id, []))

    def add_message(self, session_id: str, message: BaseMessage) -> None:
        hist = _SESSIONS[session_id]
        hist.append(message)
        max_msgs = self.max_turns * 2
        if len(hist) > max_msgs:
            del hist[:-max_msgs]

    def get_context_window(self, session_id: str, max_tokens: int = 4000) -> str:
        messages = self.get_messages(session_id)
        try:
            import tiktoken

            enc = tiktoken.get_encoding("cl100k_base")
        except Exception:
            enc = None
        parts: list[str] = []
        total = 0
        for m in reversed(messages):
            role = "用户" if isinstance(m, HumanMessage) else "助手"
            line = f"{role}: {m.content}"
            cost = len(line) if enc is None else len(enc.encode(line))
            if total + cost > max_tokens:
                break
            parts.append(line)
            total += cost
        return "\n".join(reversed(parts))
