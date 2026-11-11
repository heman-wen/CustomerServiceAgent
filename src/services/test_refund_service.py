from src.services.refund_service import check_return_window

order_id = "ORD202611080001"

result = check_return_window(order_id)

print("===== 退货期限检查 =====")
print(result)