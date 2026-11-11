from src.tools.order_tools import query_order, query_logistics


def main():
    order_id = "ORD202611080001"

    print("===== 测试：查询自己的订单 =====")
    print(query_order.invoke({"order_id": order_id}))

    print("\n===== 测试：查询自己的物流 =====")
    print(query_logistics.invoke({"order_id": order_id}))

    print("\n===== 测试：尝试查询其他用户的订单 =====")
    other_order_id = "ORD202611080003"
    print(query_order.invoke({"order_id": other_order_id}))


if __name__ == "__main__":
    main()