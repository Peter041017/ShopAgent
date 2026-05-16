from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph

from src.agent.edges.routers import route_after_intent, route_after_security, route_after_tool
from src.agent.nodes.clarification import clarification_node
from src.agent.nodes.intent_router import intent_router_node
from src.agent.nodes.memory_node import memory_context_node
from src.agent.nodes.rag_node import rag_node
from src.agent.nodes.response_gen import response_generation_node
from src.agent.nodes.security import security_node
from src.agent.nodes.tool_node import tool_executor_node
from src.agent.state import AgentState


def build_agent_graph() -> StateGraph:
    workflow = StateGraph(AgentState)

    # 安全审核（匹配开发文档决策流：安全审核 → 拒绝+提示 / 通过）
    workflow.add_node("security", security_node)
    # 对话记忆加载（匹配开发文档：对话管理 & 记忆系统）
    workflow.add_node("memory_context", memory_context_node)
    workflow.add_node("intent_router", intent_router_node)
    workflow.add_node("rag_retrieval", rag_node)
    workflow.add_node("tool_executor", tool_executor_node)
    workflow.add_node("clarification", clarification_node)
    workflow.add_node("response_gen", response_generation_node)

    # 入口：先安全审核
    workflow.add_conditional_edges(
        "security",
        route_after_security,
        {
            "rejected": END,
            "passed": "memory_context",
        },
    )
    workflow.add_edge(START, "security")

    # 记忆加载 → 意图识别
    workflow.add_edge("memory_context", "intent_router")

    workflow.add_conditional_edges(
        "intent_router",
        route_after_intent,
        {
            "rag": "rag_retrieval",
            "tool": "tool_executor",
            "clarify": "clarification",
            "respond": "response_gen",
        },
    )

    workflow.add_edge("rag_retrieval", "response_gen")

    workflow.add_conditional_edges(
        "tool_executor",
        route_after_tool,
        {
            "respond": "response_gen",
            "clarify": "clarification",
        },
    )

    workflow.add_edge("clarification", END)
    workflow.add_edge("response_gen", END)

    return workflow


def create_agent():
    """创建可编译执行的 Agent"""
    workflow = build_agent_graph()
    memory = MemorySaver()
    return workflow.compile(checkpointer=memory)
