
from datetime import datetime, timedelta


# 模拟当前登录用户
# 后续接入 Supabase Auth 后，会从可信认证上下文获取
CURRENT_USER_ID = "user_001"


# 模拟商品数据
MOCK_PRODUCTS = [
    {
        "id": "P001",
        "name": "AirPods Pro 2",
        "price": 1899,
        "stock": 35,
        "description": "苹果第二代主动降噪无线耳机",
    },
    {
        "id": "P002",
        "name": "iPhone 17",
        "price": 5999,
        "stock": 20,
        "description": "苹果智能手机",
    },
    {
        "id": "P003",
        "name": "MacBook Air",
        "price": 8999,
        "stock": 12,
        "description": "苹果轻薄笔记本电脑",
    },
]


# 模拟订单数据
MOCK_ORDERS = [
    {
        "id": "ORD202611080001",
        "user_id": "user_001",
        "status": "已签收",
        "total_amount": 1899,
        "tracking_number": "SF1234567890",
        "logistics_status": "已签收",
        "logistics_description": "包裹已由本人签收",
        "created_at": datetime.now() - timedelta(days=3),
        "refunded": False,
        "return_window_days": 7,
    },
    {
        "id": "ORD202611080002",
        "user_id": "user_001",
        "status": "运输中",
        "total_amount": 5999,
        "tracking_number": "SF9876543210",
        "logistics_status": "运输中",
        "logistics_description": "包裹正在配送途中，预计明天送达",
        "created_at": datetime.now() - timedelta(days=1),
        "refunded": False,
        "return_window_days": 7,
    },
    {
        "id": "ORD202611080003",
        "user_id": "user_002",
        "status": "已签收",
        "total_amount": 8999,
        "tracking_number": "YT1234567890",
        "logistics_status": "已签收",
        "logistics_description": "包裹已签收",
        "created_at": datetime.now() - timedelta(days=2),
        "refunded": False,
        "return_window_days": 7,
    },
]


# 模拟客服工单
MOCK_TICKETS = []
