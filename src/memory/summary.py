from langchain_core.messages import BaseMessage, HumanMessage
from langchain_openai import ChatOpenAI

from src.config.settings import settings


class SummaryMemory:
    """对超过窗口的消息做摘要压缩，保留关键信息"""

    def __init__(self) -> None:
        self.llm = ChatOpenAI(
            model=settings.LLM_MODEL,
            temperature=0.2,
            api_key=settings.OPENAI_API_KEY or None,
            base_url=settings.OPENAI_BASE_URL or None,
        )

    def summarize(self, messages: list[BaseMessage]) -> str:
        """对历史对话生成摘要"""
        prompt = "请用 2-3 句话总结以下对话，保留用户需求和关键信息:\n\n"
        lines: list[str] = []
        for m in messages:
            if isinstance(m, HumanMessage):
                lines.append(f"用户: {m.content}")
            else:
                lines.append(f"客服: {m.content}")
        history = "\n".join(lines)
        response = self.llm.invoke(prompt + history)
        return str(response.content)
