import pytest
from langchain_core.messages import HumanMessage

from src.agent.graph import create_agent


@pytest.mark.asyncio
async def test_chat_without_llm_key_still_returns(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("DEEPSEEK_API_KEY", raising=False)
    from src.config.settings import get_settings
    get_settings.cache_clear()

    agent = create_agent()
    config = {"configurable": {"thread_id": "test-002", "user_id": "u1"}}
    result = await agent.ainvoke(
        {
            "messages": [HumanMessage(content="你好")],
            "user_id": "u1",
            "session_id": "test-002",
        },
        config=config,
    )
    assert "final_response" in result
    assert len(result["final_response"]) > 0


@pytest.mark.asyncio
async def test_agent_product_inquiry_no_llk(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("DEEPSEEK_API_KEY", raising=False)
    from src.config.settings import get_settings
    get_settings.cache_clear()

    agent = create_agent()
    config = {"configurable": {"thread_id": "test-003", "user_id": "u1"}}
    result = await agent.ainvoke(
        {
            "messages": [HumanMessage(content="iPhone 16 Pro 有什么颜色")],
            "user_id": "u1",
            "session_id": "test-003",
        },
        config=config,
    )
    assert "final_response" in result


@pytest.mark.asyncio
async def test_agent_order_query_no_llk(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("DEEPSEEK_API_KEY", raising=False)
    from src.config.settings import get_settings
    get_settings.cache_clear()

    agent = create_agent()
    config = {"configurable": {"thread_id": "test-004", "user_id": "user_001"}}
    result = await agent.ainvoke(
        {
            "messages": [HumanMessage(content="查询我的订单列表")],
            "user_id": "user_001",
            "session_id": "test-004",
        },
        config=config,
    )
    assert "final_response" in result
    # 无 LLM 时工具结果应直接返回
    resp = result.get("final_response", "")
    assert len(resp) > 0


@pytest.mark.asyncio
async def test_agent_refund_no_llk(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("DEEPSEEK_API_KEY", raising=False)
    from src.config.settings import get_settings
    get_settings.cache_clear()

    agent = create_agent()
    config = {"configurable": {"thread_id": "test-005", "user_id": "user_002"}}
    result = await agent.ainvoke(
        {
            "messages": [HumanMessage(content="我要退款 ORD-20260514-001")],
            "user_id": "user_002",
            "session_id": "test-005",
        },
        config=config,
    )
    assert "final_response" in result
