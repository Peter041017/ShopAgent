import pytest

from src.tools.logistics_tools import track_logistics
from src.tools.order_tools import list_user_orders, query_order
from src.tools.product_tools import search_products
from src.tools.refund_tools import query_refund_policy, submit_refund


@pytest.mark.asyncio
async def test_query_order_found():
    out = await query_order.ainvoke({"order_id": "ORD-20260501-001", "user_id": "user_001"})
    assert "张三" in out
    assert "已送达" in out
    assert "ORD-20260501-001" in out


@pytest.mark.asyncio
async def test_query_order_not_found():
    out = await query_order.ainvoke({"order_id": "ORD-XXXX", "user_id": "guest"})
    assert "未找到" in out or "请核对" in out


@pytest.mark.asyncio
async def test_query_order_wrong_user():
    out = await query_order.ainvoke({"order_id": "ORD-20260501-001", "user_id": "user_002"})
    assert "未找到" in out


@pytest.mark.asyncio
async def test_list_user_orders():
    out = await list_user_orders.ainvoke({"user_id": "user_001", "status_filter": "all"})
    assert "张三" in out
    assert "4" in out or "四" in out


@pytest.mark.asyncio
async def test_list_user_orders_empty():
    out = await list_user_orders.ainvoke({"user_id": "user_999", "status_filter": "all"})
    assert "暂无订单" in out


@pytest.mark.asyncio
async def test_search_products():
    out = await search_products.ainvoke({
        "keyword": "iPhone",
        "category": "",
        "price_min": 0,
        "price_max": 999999,
    })
    assert "iPhone 16 Pro" in out
    assert "找到" in out


@pytest.mark.asyncio
async def test_search_products_no_results():
    out = await search_products.ainvoke({
        "keyword": "不存在商品",
        "category": "",
        "price_min": 0,
        "price_max": 999999,
    })
    assert "未找到" in out


@pytest.mark.asyncio
async def test_track_logistics_found():
    out = await track_logistics.ainvoke({"tracking_number": "SF1487654321"})
    assert "顺丰速运" in out
    assert "已签收" in out


@pytest.mark.asyncio
async def test_track_logistics_not_found():
    out = await track_logistics.ainvoke({"tracking_number": "SF0000000000"})
    assert "未找到" in out


@pytest.mark.asyncio
async def test_query_refund_policy():
    out = await query_refund_policy.ainvoke({"product_category": "手机"})
    assert "7 天无理由" in out


@pytest.mark.asyncio
async def test_submit_refund():
    out = await submit_refund.ainvoke({"order_id": "ORD-20260512-001", "reason": "不想要了"})
    assert "已收到" in out
    assert "ORD-20260512-001" in out


@pytest.mark.asyncio
async def test_submit_refund_not_found():
    out = await submit_refund.ainvoke({"order_id": "ORD-XXXX", "reason": "测试"})
    assert "未找到" in out
