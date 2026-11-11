from src.database.supabase_client import get_supabase
from src.core.security import DEV_USER_ID


def get_owned_order(order_id: str, user_id: str = DEV_USER_ID) -> dict | None:
    """
    查询当前用户自己的订单。

    同时使用订单 ID 和用户 ID 作为数据库过滤条件，
    不先查询订单再在 Python 中判断归属。
    """

    if not order_id or not order_id.strip():
        return None

    response = (
        get_supabase()
        .table("orders")
        .select(
            "id, user_id, status, total_amount, tracking_number, "
            "logistics_status, logistics_description, created_at, "
            "refunded, return_window_days,delivered_at"
        )
        .eq("id", order_id.strip())
        .eq("user_id", user_id)
        .limit(1)
        .execute()
    )

    orders = response.data or []
    return orders[0] if orders else None