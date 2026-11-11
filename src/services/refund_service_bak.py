
from datetime import datetime, timezone

from src.services.order_service import get_owned_order
from datetime import datetime, timezone, timedelta

def check_return_window(order: dict, return_window_days: int = 7, reason: str = "")  -> dict:
    """
    根据实际签收时间检查退货期限。
    """
    
    delivered_at = order.get("delivered_at")
    if not delivered_at:
        return {
            "eligible": None,
            "message": "订单缺少实际签收时间，暂时无法确认是否在退货期限内。",
        }
    delivered_time = datetime.fromisoformat(
        delivered_at.replace("Z", "+00:00")
    )

    now = datetime.now(timezone.utc)

    deadline = delivered_time + timedelta(days=return_window_days)
    if now > deadline:
        return {
            "eligible": False,
            "message": f"已超过 {return_window_days} 天的退款期限,需要人工客服进一步审核。",
        }

    return {
        "eligible": True,
        "message": (
            f"该订单仍在签收后 7 天的退货期限内。退款原因：{reason.strip()}。"
            "注意：目前仅完成资格检查，尚未提交退款申请。"
        ),
    }



def check_refund_eligibility(order_id: str, reason: str) -> dict:
    """检查订单是否符合退款条件，不执行实际退款。"""

    if not reason or not reason.strip():
        return {
            "eligible": False,
            "message": "请提供退款原因。",
        }

    order = get_owned_order(order_id)
    if not order:
        return {
            "eligible": False,
            "message": "未找到该订单，或当前用户无权查看该订单。",
        }

    if order.get("refunded"):
        return {
            "eligible": False,
            "message": "该订单已经退款，不能重复申请。",
        }

    if order.get("status") != "已签收":
        return {
            "eligible": False,
            "message": "当前订单尚未签收，暂不符合本系统的退款条件。",
        }



    return check_return_window(order, 7, reason)
