from sqlalchemy import select

from langchain_core.tools import tool
from pydantic import BaseModel, Field

from src.database.engine import get_session
from src.database.models import Order, Refund


class RefundPolicyInput(BaseModel):
    product_category: str = Field(default="general", description="商品类目")


class SubmitRefundInput(BaseModel):
    order_id: str = Field(description="订单号")
    reason: str = Field(description="退款原因")


@tool(args_schema=RefundPolicyInput)
async def query_refund_policy(product_category: str = "general") -> str:
    """查询退换货与退款政策说明"""
    return (
        f"类目「{product_category}」退换货政策：\n"
        "- 7 天无理由退货（未拆封，包装完好）\n"
        "- 质量问题 15 天可退可换\n"
        "- 退款质检通过后 1-3 个工作日原路退回\n"
        "- 非质量问题退货运费由用户承担（含运费险补贴）\n"
        "- 质量问题运费由平台承担\n\n"
        "详细政策请参考知识库中的退换货政策文档。"
    )


@tool(args_schema=SubmitRefundInput)
async def submit_refund(order_id: str, reason: str) -> str:
    """提交退款申请"""
    async with get_session() as session:
        order = (
            await session.execute(select(Order).where(Order.order_no == order_id))
        ).scalar_one_or_none()

        if not order:
            return f"未找到订单 {order_id}，请核对订单号后重试。"

        if order.status in ("cancelled",):
            return f"订单 {order_id} 已取消，无法提交退款申请。"

        if order.status == "pending":
            return f"订单 {order_id} 尚未付款，无需退款。如需取消请取消订单。"

        try:
            import uuid

            refund_id = uuid.uuid4().hex[:12]
            session.add(
                Refund(
                    id=refund_id,
                    order_id=order.id,
                    user_id=order.user_id,
                    amount=order.total_amount,
                    reason=reason,
                    status="pending",
                )
            )
            await session.commit()
        except Exception:
            await session.rollback()
            return f"提交退款申请失败，请稍后重试或联系人工客服。"

        return (
            f"已收到订单 {order_id} 的退款申请，"
            f"原因：{reason}。\n"
            f"退款金额：¥{order.total_amount:.2f}\n"
            f"客服将在 24 小时内处理，处理结果将通过站内信通知您。"
        )
