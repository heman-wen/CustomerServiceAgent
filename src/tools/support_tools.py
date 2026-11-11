
from langchain.tools import tool

from src.services.ticket_service import create_ticket
from src.core.tool_result import (
    success,
    not_found,
    failed,
    unknown,
)


@tool
def create_support_ticket(
    issue_type: str,
    description: str,
    order_id: str = "",
    priority: str = "normal",
) -> dict:
    """
    创建客服工单。可关联订单，支持 low、normal、high 三种优先级。
    """

    try:
        ticket = create_ticket(
            issue_type=issue_type,
            description=description,
            order_id=order_id,
            priority=priority,
        )

        status_text = {
            "open": "待处理",
            "processing": "处理中",
            "closed": "已关闭",
        }.get(ticket["status"], ticket["status"])

        ticket_data = {
            "ticket_id": ticket["id"],
            "issue_type": ticket["issue_type"],
            "status": ticket["status"],
            "status_text": status_text,
            "priority": ticket["priority"],
            "order_id": ticket.get("order_id"),
        }

        return success(
            data=ticket_data,
            message=(
                "客服工单创建成功，当前状态为待处理。"
                "工单已保存，但尚未实现人工客服通知或自动分配。"
            ),
        )

    except ValueError as e:
        error_message = str(e)

        # 关联订单不存在或无权访问
        if "未找到该订单" in error_message:
            return not_found(
                message=error_message
            )

        # 其他参数或业务校验错误
        return unknown(
            message=error_message
        )

    except Exception as e:
        print(
            f"[Support Ticket Tool Error] {type(e).__name__}: {e}"
        )

        return failed(
            message="工单创建服务暂时不可用，请稍后重试。"
        )
