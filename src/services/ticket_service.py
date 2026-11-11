
from src.database.supabase_client import get_supabase
from src.core.security import DEV_USER_ID
from src.services.order_service import get_owned_order


def create_ticket(
    issue_type: str,
    description: str,
    order_id: str = "",
    priority: str = "normal",
) -> dict:
    """创建客服工单并保存到 Supabase。"""

    if not description or not description.strip():
        raise ValueError("工单描述不能为空")

    if priority not in ("low", "normal", "high"):
        raise ValueError("工单优先级只能是 low、normal 或 high")

    # 如果关联订单，必须确认订单属于当前用户
    if order_id:
        order = get_owned_order(order_id)

        if not order:
            raise ValueError("未找到该订单，或当前用户无权关联该订单")

    payload = {
        "user_id": DEV_USER_ID,
        "order_id": order_id or None,
        "issue_type": issue_type,
        "description": description.strip(),
        "priority": priority,
        "status": "open",
    }

    response = (
        get_supabase()
        .table("support_tickets")
        .insert(payload)
        .execute()
    )

    tickets = response.data or []

    if not tickets:
        raise RuntimeError("工单创建失败，数据库未返回记录")

    return tickets[0]
