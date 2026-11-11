from types import SimpleNamespace
from unittest.mock import MagicMock

from src.services.product_service import (
    get_product_by_name,
    get_product_by_id,
)


def create_mock_supabase(monkeypatch, data):
    """
    创建模拟 Supabase 客户端。

    data：模拟数据库返回的数据。
    """
    mock_supabase = MagicMock()
    mock_query = MagicMock()

    # 模拟 Supabase 查询链式调用
    mock_supabase.table.return_value = mock_query

    mock_query.select.return_value = mock_query
    mock_query.ilike.return_value = mock_query
    mock_query.eq.return_value = mock_query
    mock_query.limit.return_value = mock_query

    # 模拟 execute() 返回结果
    mock_query.execute.return_value = SimpleNamespace(data=data)

    # 替换 product_service 中的 get_supabase
    monkeypatch.setattr(
        "src.services.product_service.get_supabase",
        lambda: mock_supabase,
    )

    return mock_supabase, mock_query


# ==============================
# 按商品名称查询
# ==============================

def test_get_product_by_name_success(monkeypatch):
    """测试：根据名称成功查询商品。"""

    mock_products = [
        {
            "id": "P001",
            "name": "AirPods Pro 2",
            "description": "苹果第二代主动降噪无线耳机",
            "price": 1899.0,
            "stock": 35,
            "category": "耳机",
            "status": "active",
        }
    ]

    mock_supabase, mock_query = create_mock_supabase(
        monkeypatch,
        mock_products,
    )

    result = get_product_by_name("AirPods")

    assert result == mock_products

    # 验证数据库查询条件
    mock_supabase.table.assert_called_once_with("products")

    mock_query.ilike.assert_called_once_with(
        "name",
        "%AirPods%",
    )

    mock_query.eq.assert_called_once_with(
        "status",
        "active",
    )

    mock_query.limit.assert_called_once_with(10)

    mock_query.execute.assert_called_once()


def test_get_product_by_name_empty():
    """测试：商品名称为空。"""

    mock_supabase = MagicMock()

    # 空字符串不应该访问数据库
    result = get_product_by_name("")

    assert result == []


def test_get_product_by_name_whitespace():
    """测试：商品名称只有空格。"""

    result = get_product_by_name("   ")

    assert result == []


def test_get_product_by_name_not_found(monkeypatch):
    """测试：没有查询到匹配商品。"""

    create_mock_supabase(monkeypatch, [])

    result = get_product_by_name("不存在的商品")

    assert result == []


# ==============================
# 按商品 ID 查询
# ==============================

def test_get_product_by_id_success(monkeypatch):
    """测试：根据 ID 成功查询商品。"""

    mock_product = {
        "id": "P001",
        "name": "AirPods Pro 2",
        "description": "苹果第二代主动降噪无线耳机",
        "price": 1899.0,
        "stock": 35,
        "category": "耳机",
        "status": "active",
    }

    mock_supabase, mock_query = create_mock_supabase(
        monkeypatch,
        [mock_product],
    )

    result = get_product_by_id("P001")

    assert result == mock_product

    mock_supabase.table.assert_called_once_with("products")

    mock_query.eq.assert_any_call("id", "P001")
    mock_query.eq.assert_any_call("status", "active")

    mock_query.limit.assert_called_once_with(1)

    mock_query.execute.assert_called_once()


def test_get_product_by_id_empty():
    """测试：商品 ID 为空。"""

    result = get_product_by_id("")

    assert result is None


def test_get_product_by_id_whitespace():
    """测试：商品 ID 只有空格。"""

    result = get_product_by_id("   ")

    assert result is None


def test_get_product_by_id_not_found(monkeypatch):
    """测试：没有查询到商品。"""

    create_mock_supabase(monkeypatch, [])

    result = get_product_by_id("P999")

    assert result is None