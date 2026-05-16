from src.agent.state import AgentState
from src.rag.retriever import HybridRetriever


async def rag_node(state: AgentState) -> dict:
    last = state["messages"][-1]
    query = last.content if hasattr(last, "content") else str(last)
    retriever = HybridRetriever()
    try:
        docs = retriever.retrieve(str(query), top_k=5)
    except Exception:
        docs = []
    serialized = [
        {"page_content": d.page_content, "metadata": dict(d.metadata)} for d in docs
    ]
    return {"retrieved_docs": serialized}
