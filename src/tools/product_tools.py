from sqlalchemy import select

from langchain_core.tools import tool
from pydantic import BaseModel, Field

from src.database.engine import get_session
from src.database.models import Product


class ProductSearchInput(BaseModel):
    keyword: str = Field(description="搜索关键词")
    category: str = Field(default="", description="商品分类")
    price_min: float = Field(default=0, description="最低价格")
    price_max: float = Field(default=999999, description="最高价格")


@tool(args_schema=ProductSearchInput)
async def search_products(
    keyword: str,
    category: str = "",
    price_min: float = 0,
    price_max: float = 999999,
) -> str:
    """搜索商品，支持关键词、分类、价格区间筛选"""
    async with get_session() as session:
        stmt = select(Product).where(Product.price >= price_min, Product.price <= price_max)

        if keyword:
            like = f"%{keyword}%"
            stmt = stmt.where(
                Product.name.ilike(like) | Product.description.ilike(like)
            )
        if category:
            stmt = stmt.where(Product.category == category)

        stmt = stmt.order_by(Product.price.asc())
        products = (await session.execute(stmt)).scalars().all()

        if not products:
            parts = [f"关键词「{keyword}」" if keyword else ""]
            if category:
                parts.append(f"分类「{category}」")
            parts.append(f"价格 {price_min}-{price_max}")
            return f"未找到匹配的商品（{'，'.join(parts)}）。"

        lines = [
            f"搜索「{keyword}」的结果：找到 {len(products)} 件商品"
            + (f"（分类: {category}" if category else "（全部")
            + f"，价格 {price_min}-{price_max}）。"
        ]
        for p in products[:5]:
            lines.append(f"\n【{p.name}】")
            lines.append(f"  价格: ¥{p.price:.2f}  |  库存: {p.stock}")
            if p.description:
                lines.append(f"  简介: {p.description}")
            if p.specs:
                lines.append(f"  规格: {p.specs}")
        if len(products) > 5:
            lines.append(f"\n  ...以及其他 {len(products) - 5} 件商品")

        return "\n".join(lines)
