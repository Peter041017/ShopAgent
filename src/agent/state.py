from __future__ import annotations

from typing import Annotated, Literal, NotRequired, TypedDict

from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages


class AgentState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
    user_id: str
    session_id: str
    intent: NotRequired[Literal[
        "product_inquiry", "order_query", "after_sales", "chitchat", "unknown"
    ]]
    retrieved_docs: NotRequired[list]
    tool_results: NotRequired[list[dict]]
    needs_human: NotRequired[bool]
    needs_clarification: NotRequired[bool]
    clarification_question: NotRequired[str]
    slots: NotRequired[dict]
    final_response: NotRequired[str]
    # 对话上下文历史（格式化的历史消息，供生成回复使用）
    conversation_history: NotRequired[str]
    # 安全审核拦截标记（始终由 security_node 在当前轮设置）
    _security_blocked: NotRequired[bool]
