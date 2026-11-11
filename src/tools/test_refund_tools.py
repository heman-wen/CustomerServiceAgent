
from src.tools.refund_tools import check_refund_eligibility_tool


def main():
    print("===== 测试：符合退款条件 =====")
    result = check_refund_eligibility_tool.invoke({
        "order_id": "ORD202611080001",
        "reason": "商品存在质量问题",
    })
    print(result)

    print("\n===== 测试：订单尚未签收 =====")
    result = check_refund_eligibility_tool.invoke({
        "order_id": "ORD202611080002",
        "reason": "不想要了",
    })
    print(result)

    print("\n===== 测试：查询其他用户订单 =====")
    result = check_refund_eligibility_tool.invoke({
        "order_id": "ORD202611080003",
        "reason": "商品存在质量问题",
    })
    print(result)

    print("\n===== 测试：未填写退款原因 =====")
    result = check_refund_eligibility_tool.invoke({
        "order_id": "ORD202611080001",
        "reason": "",
    })
    print(result)


if __name__ == "__main__":
    main()
