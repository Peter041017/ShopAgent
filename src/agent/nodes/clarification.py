from src.agent.state import AgentState


def clarification_node(state: AgentState) -> dict:
    q = state.get("clarification_question") or "请补充更多信息，方便我为您处理。"
    return {"final_response": q}
