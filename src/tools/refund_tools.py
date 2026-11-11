
from langchain_core.tools import tool

from src.services.refund_service import (
    check_return_window,
    check_refund_eligibility,
)

from src.core.tool_result import (
    success,
    not_found,
    failed,
    unknown,
)


def format_refund_result(result: dict) -> dict:
    """将退款 Service 的返回结果转换成统一工具格式。"""

    status = result.get("status")
    message = result.get("message", "退款检查完成")

    data = {
        "eligible": result.get("eligible"),
    }

    if status == "not_found":
        return not_found(message=message)

    if status == "unknown":
        return unknown(message=message)

    if status == "success":
        return success(
            data=data,
            message=message,
        )

    return failed(
        message="退款检查返回了无法识别的结果。"
    )


@tool
def check_return_window_tool(order_id: str) -> dict:
    """
    检查订单是否在签收后7天退货期限内。
    用户询问能否退货、退货期限、是否超过退货期限时调用。
    不需要退款原因。
    """

    try:
        result = check_return_window(order_id)

        return format_refund_result(result)

    except Exception as e:
        print(
            f"[Return Window Tool Error] {type(e).__name__}: {e}"
        )

        return failed(
            message="退货期限检查服务暂时不可用，请稍后重试。"
        )


@tool
def check_refund_eligibility_tool(
    order_id: str,
    reason: str
) -> dict:
    """
    检查订单退款资格。
    只有用户明确要求申请退款或检查退款资格时调用。
    必须提供退款原因。
    """

    try:
        result = check_refund_eligibility(
            order_id,
            reason
        )

        return format_refund_result(result)

    except Exception as e:
        print(
            f"[Refund Eligibility Tool Error] {type(e).__name__}: {e}"
        )

        return failed(
            message="退款资格检查服务暂时不可用，请稍后重试。"
        )
