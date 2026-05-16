"""管理后台接口 — 健康检查、系统指标、会话管理。"""

from fastapi import APIRouter
from sqlalchemy import func, select

from src.database.engine import get_session
from src.database.models import Order, Product, Refund, User

router = APIRouter()


@router.get("/health")
async def admin_health():
    return {"status": "ok", "service": "shopagent", "version": "0.1.0"}


@router.get("/metrics")
async def system_metrics():
    """系统概览指标"""
    async with get_session() as session:
        user_count = (await session.execute(select(func.count(User.id)))).scalar() or 0
        product_count = (await session.execute(select(func.count(Product.id)))).scalar() or 0
        order_count = (await session.execute(select(func.count(Order.id)))).scalar() or 0
        refund_count = (await session.execute(select(func.count(Refund.id)))).scalar() or 0

        pending_orders = (
            await session.execute(
                select(func.count(Order.id)).where(Order.status == "pending")
            )
        ).scalar() or 0

        pending_refunds = (
            await session.execute(
                select(func.count(Refund.id)).where(Refund.status == "pending")
            )
        ).scalar() or 0

        # 营业额统计
        total_revenue = (
            await session.execute(
                select(func.coalesce(func.sum(Order.total_amount), 0)).where(
                    Order.status.in_(["paid", "shipped", "delivered"])
                )
            )
        ).scalar() or 0.0

    return {
        "users": user_count,
        "products": product_count,
        "orders": {
            "total": order_count,
            "pending": pending_orders,
        },
        "refunds": {
            "total": refund_count,
            "pending": pending_refunds,
        },
        "revenue": round(float(total_revenue), 2),
    }


@router.get("/orders")
async def list_orders(limit: int = 20, offset: int = 0):
    """订单列表（管理后台用）"""
    async with get_session() as session:
        stmt = select(Order).order_by(Order.created_at.desc()).limit(limit).offset(offset)
        orders = (await session.execute(stmt)).scalars().all()
    return [
        {
            "order_no": o.order_no,
            "user_id": o.user_id,
            "total_amount": o.total_amount,
            "status": o.status,
            "created_at": o.created_at.isoformat() if o.created_at else None,
        }
        for o in orders
    ]


@router.get("/refunds")
async def list_refunds(limit: int = 20, offset: int = 0):
    """退款列表"""
    async with get_session() as session:
        stmt = select(Refund).order_by(Refund.created_at.desc()).limit(limit).offset(offset)
        refunds = (await session.execute(stmt)).scalars().all()
    return [
        {
            "id": r.id,
            "order_id": r.order_id,
            "user_id": r.user_id,
            "amount": r.amount,
            "reason": r.reason,
            "status": r.status,
            "created_at": r.created_at.isoformat() if r.created_at else None,
        }
        for r in refunds
    ]
