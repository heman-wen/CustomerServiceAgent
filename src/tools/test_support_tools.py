
from src.tools.support_tools import create_support_ticket


def main():
    print("===== 测试：创建关联订单的工单 =====")

    result = create_support_ticket.invoke({
        "issue_type": "商品质量问题",
        "description": "用户反馈 AirPods Pro 2 左耳没有声音，希望客服协助处理。",
        "order_id": "ORD202611080001",
        "priority": "high",
    })

    print(result)

    print("\n===== 测试：关联其他用户的订单 =====")

    result = create_support_ticket.invoke({
        "issue_type": "退款问题",
        "description": "尝试关联其他用户的订单。",
        "order_id": "ORD202611080003",
        "priority": "normal",
    })

    print(result)

    print("\n===== 测试：创建不关联订单的工单 =====")

    result = create_support_ticket.invoke({
        "issue_type": "使用咨询",
        "description": "用户咨询商品的使用方法。",
        "priority": "normal",
    })

    print(result)


if __name__ == "__main__":
    main()
