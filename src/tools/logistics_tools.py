from sqlalchemy import select
from sqlalchemy.orm import selectinload

from langchain_core.tools import tool
from pydantic import BaseModel, Field

from src.database.engine import get_session
from src.database.models import Logistics, LogisticsTrack


class TrackInput(BaseModel):
    tracking_number: str = Field(description="物流单号")


@tool(args_schema=TrackInput)
async def track_logistics(tracking_number: str) -> str:
    """根据物流单号查询物流轨迹"""
    async with get_session() as session:
        logistics = (
            await session.execute(
                select(Logistics)
                .options(selectinload(Logistics.tracks))
                .where(Logistics.tracking_no == tracking_number)
            )
        ).scalar_one_or_none()

        if not logistics:
            return f"未找到单号 {tracking_number} 的物流信息，请核对物流单号后重试。"

        tracks = sorted(logistics.tracks, key=lambda t: t.timestamp)

        lines = [
            f"运单 {tracking_number}",
            f"快递公司: {logistics.carrier}",
            f"当前状态: {TRACK_STATUS_LABELS.get(logistics.status, logistics.status)}",
        ]
        if tracks:
            lines.append("\n物流轨迹:")
            for t in tracks:
                time_str = t.timestamp.strftime("%m-%d %H:%M")
                lines.append(f"  [{time_str}] {t.message}")
        else:
            lines.append("\n暂无物流轨迹信息。")

        return "\n".join(lines)


TRACK_STATUS_LABELS = {
    "pending": "待揽收",
    "picked_up": "已揽收",
    "in_transit": "运输中",
    "delivering": "派送中",
    "delivered": "已签收",
}
