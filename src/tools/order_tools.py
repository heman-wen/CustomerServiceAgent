
from langchain.tools import tool

from src.services.order_service import get_owned_order
from src.core.tool_result import (
    success,
    not_found,
    failed,
)


@tool
def query_order(order_id: str) -> dict:
    """
    查询当前用户指定订单的状态、金额和下单时间。
    """

    try:
        order = get_owned_order(order_id)

        if not order:
            return not_found(
                message="未找到该订单，或当前用户无权查看该订单。"
            )

        order_data = {
            "order_id": order["id"],
            "status": order["status"],
            "total_amount": order["total_amount"],
            "created_at": order["created_at"],
        }

        return success(
            data=order_data,
            message="订单查询成功。"
        )

    except Exception as e:
        print(
            f"[Order Tool Error] {type(e).__name__}: {e}"
        )

        return failed(
            message="订单查询服务暂时不可用，请稍后重试。"
        )


@tool
def query_logistics(order_id: str) -> dict:
    """
    查询当前用户指定订单的物流单号、物流状态和物流信息。
    """

    try:
        order = get_owned_order(order_id)

        if not order:
            return not_found(
                message="未找到该订单，或当前用户无权查看该订单。"
            )

        logistics_data = {
            "order_id": order["id"],
            "tracking_number": (
                order.get("tracking_number") or "暂无物流单号"
            ),
            "logistics_status": (
                order.get("logistics_status") or "暂无物流状态"
            ),
            "logistics_description": (
                order.get("logistics_description") or "暂无物流信息"
            ),
        }

        return success(
            data=logistics_data,
            message="物流信息查询成功。"
        )

    except Exception as e:
        print(
            f"[Logistics Tool Error] {type(e).__name__}: {e}"
        )

        return failed(
            message="物流查询服务暂时不可用，请稍后重试。"
        )
