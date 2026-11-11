
from src.database.supabase_client import get_supabase


def get_product_by_name(product_name: str) -> list[dict]:
    """根据商品名称模糊查询商品。"""

    if not product_name or not product_name.strip():
        return []

    response = (
        get_supabase()
        .table("products")
        .select("id, name, description, price, stock, category, status")
        .ilike("name", f"%{product_name.strip()}%")
        .eq("status", "active")
        .limit(10)
        .execute()
    )

    return response.data or []


def get_product_by_id(product_id: str) -> dict | None:
    """根据商品 ID 查询单个商品。"""

    if not product_id or not product_id.strip():
        return None

    response = (
        get_supabase()
        .table("products")
        .select("id, name, description, price, stock, category, status")
        .eq("id", product_id.strip())
        .eq("status", "active")
        .limit(1)
        .execute()
    )

    products = response.data or []
    return products[0] if products else None
