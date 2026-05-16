from sqlalchemy import select
from sqlalchemy.orm import selectinload

from langchain_core.tools import tool
from pydantic import BaseModel, Field

from src.database.engine import get_session
from src.database.models import Logistics, Order, OrderItem, Product, User


class OrderQueryInput(BaseModel):
    order_id: str = Field(description="订单号")
    user_id: str = Field(description="用户ID")


class OrderStatusInput(BaseModel):
    user_id: str = Field(description="用户ID")
    status_filter: str = Field(
        default="all",
        description="订单状态筛选：pending/paid/shipped/delivered/cancelled",
    )


@tool(args_schema=OrderQueryInput)
async def query_order(order_id: str, user_id: str) -> str:
    """查询指定订单的详细信息，包括商品、金额、状态、物流等"""
    async with get_session() as session:
        stmt = select(Order).where(Order.order_no == order_id)
        if user_id != "guest":
            stmt = stmt.where(Order.user_id == user_id)
        order = (await session.execute(stmt)).scalar_one_or_none()

        if not order:
            return f"未找到订单 {order_id}，请核对订单号后重试。"

        user = (
            await session.execute(select(User).where(User.id == order.user_id))
        ).scalar_one_or_none()
        display_name = user.display_name if user else user_id

        items_result = await session.execute(
            select(OrderItem, Product)
            .join(Product, OrderItem.product_id == Product.id)
            .where(OrderItem.order_id == order.id)
        )
        item_lines = []
        for order_item, product in items_result:
            item_lines.append(
                f"{product.name} x{order_item.quantity}  ¥{order_item.price:.2f}"
            )

        logistics = (
            await session.execute(
                select(Logistics)
                .options(selectinload(Logistics.tracks))
                .where(Logistics.order_id == order.id)
            )
        ).scalar_one_or_none()

        lines = [
            f"订单号: {order.order_no}",
            f"用户: {display_name}",
            f"状态: {STATUS_LABELS.get(order.status, order.status)}",
            f"商品: {' / '.join(item_lines)}",
            f"金额: ¥{order.total_amount:.2f}",
            f"下单时间: {order.created_at.strftime('%Y-%m-%d %H:%M')}",
        ]
        if logistics:
            lines.append(f"物流: {logistics.carrier} {logistics.tracking_no}")
        if order.shipping_address:
            lines.append(f"收货地址: {order.shipping_address}")
        if logistics and logistics.tracks:
            last_track = sorted(logistics.tracks, key=lambda t: t.timestamp)[-1]
            lines.append(f"物流状态: {last_track.message}")

        return "\n".join(lines)


@tool(args_schema=OrderStatusInput)
async def list_user_orders(user_id: str, status_filter: str = "all") -> str:
    """查询用户订单列表，可按状态筛选"""
    async with get_session() as session:
        user = (
            await session.execute(select(User).where(User.id == user_id))
        ).scalar_one_or_none()
        display_name = user.display_name if user else user_id

        stmt = select(Order).where(Order.user_id == user_id)
        if status_filter != "all":
            stmt = stmt.where(Order.status == status_filter)
        stmt = stmt.order_by(Order.created_at.desc())
        orders = (await session.execute(stmt)).scalars().all()

        if not orders:
            return (
                f"用户 {display_name} 暂无订单。"
                if status_filter == "all"
                else f"用户 {display_name} 没有{STATUS_LABELS.get(status_filter, status_filter)}状态的订单。"
            )

        order_lines = [f"用户 {display_name} 的订单列表（筛选: {status_filter}）：共 {len(orders)} 笔订单。"]
        for o in orders:
            order_lines.append(f"  {o.order_no}  {STATUS_LABELS.get(o.status, o.status)}  ¥{o.total_amount:.2f}")

        return "\n".join(order_lines)


STATUS_LABELS = {
    "pending": "待付款",
    "paid": "已付款",
    "shipped": "已发货",
    "delivered": "已送达",
    "cancelled": "已取消",
}
