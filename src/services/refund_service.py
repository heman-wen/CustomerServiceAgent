
from datetime import datetime, timezone, timedelta

from src.services.order_service import get_owned_order


def check_return_window(
    order_id: str,
    return_window_days: int = 7
) -> dict:
    """根据订单实际签收时间检查退货期限。"""

    order = get_owned_order(order_id)

    if not order:
        return {
            "status": "not_found",
            "eligible": None,
            "message": "未找到该订单，或当前用户无权查看该订单。",
        }

    if order.get("status") != "已签收":
        return {
            "status": "success",
            "eligible": False,
            "message": "当前订单尚未签收，暂不符合退货期限检查条件。",
        }

    delivered_at = order.get("delivered_at")

    if not delivered_at:
        return {
            "status": "unknown",
            "eligible": None,
            "message": "订单缺少实际签收时间，暂时无法确认是否在退货期限内。",
        }

    if isinstance(delivered_at, str):
        delivered_time = datetime.fromisoformat(
            delivered_at.replace("Z", "+00:00")
        )
    else:
        delivered_time = delivered_at

    now = datetime.now(timezone.utc)

    deadline = delivered_time + timedelta(days=return_window_days)

    if now > deadline:
        return {
            "status": "success",
            "eligible": False,
            "message": (
                f"已超过签收后 {return_window_days} 天的退货期限，"
                "需要人工客服进一步审核。"
            ),
        }

    return {
        "status": "success",
        "eligible": True,
        "message": (
            f"该订单仍在签收后 {return_window_days} 天的退货期限内。"
        ),
    }


def check_refund_eligibility(order_id: str, reason: str) -> dict:
    """检查订单是否符合退款条件，不执行实际退款。"""

    if not reason or not reason.strip():
        return {
            "status": "unknown",
            "eligible": None,
            "message": "请提供退款原因。",
        }

    order = get_owned_order(order_id)

    if not order:
        return {
            "status": "not_found",
            "eligible": None,
            "message": "未找到该订单，或当前用户无权查看该订单。",
        }

    if order.get("refunded"):
        return {
            "status": "success",
            "eligible": False,
            "message": "该订单已经退款，不能重复申请。",
        }

    if order.get("status") != "已签收":
        return {
            "status": "success",
            "eligible": False,
            "message": "当前订单尚未签收，暂不符合本系统的退款条件。",
        }

    # 先检查退货期限
    window_result = check_return_window(order_id)

    if window_result["status"] != "success":
        return window_result

    if window_result["eligible"] is not True:
        return {
            "status": "success",
            "eligible": False,
            "message": window_result["message"],
        }

    return {
        "status": "success",
        "eligible": True,
        "message": (
            f"退款原因：{reason.strip()}。"
            "订单符合当前系统的退款资格检查条件，"
            "但退款申请尚未提交。"
        ),
    }
