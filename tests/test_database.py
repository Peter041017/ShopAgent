import pytest
from sqlalchemy import select, text

from src.database.engine import get_engine, get_session
from src.database.models import Order, Product, Refund, User


@pytest.mark.asyncio
async def test_users_seeded():
    async with get_session() as session:
        users = (await session.execute(select(User))).scalars().all()
        assert len(users) == 3


@pytest.mark.asyncio
async def test_products_seeded():
    async with get_session() as session:
        products = (await session.execute(select(Product))).scalars().all()
        assert len(products) == 10


@pytest.mark.asyncio
async def test_orders_seeded():
    async with get_session() as session:
        orders = (await session.execute(select(Order))).scalars().all()
        assert len(orders) == 10


@pytest.mark.asyncio
async def test_refunds_seeded():
    async with get_session() as session:
        refunds = (await session.execute(select(Refund))).scalars().all()
        assert len(refunds) >= 2  # 种子 2 条 + 工具测试可能新增


@pytest.mark.asyncio
async def test_user_zhangsan_has_orders():
    async with get_session() as session:
        orders = (
            await session.execute(
                select(Order).where(Order.user_id == "user_001")
            )
        ).scalars().all()
        assert len(orders) == 4
        statuses = {o.status for o in orders}
        assert "delivered" in statuses
        assert "shipped" in statuses
        assert "paid" in statuses
        assert "cancelled" in statuses
