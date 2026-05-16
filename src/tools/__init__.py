from src.tools.logistics_tools import track_logistics
from src.tools.order_tools import list_user_orders, query_order
from src.tools.product_tools import search_products
from src.tools.refund_tools import query_refund_policy, submit_refund

ALL_TOOLS = [
    query_order,
    list_user_orders,
    search_products,
    track_logistics,
    query_refund_policy,
    submit_refund,
]

DANGEROUS_TOOLS = {submit_refund.name}

__all__ = [
    "ALL_TOOLS",
    "DANGEROUS_TOOLS",
    "query_order",
    "list_user_orders",
    "search_products",
    "track_logistics",
    "query_refund_policy",
    "submit_refund",
]
