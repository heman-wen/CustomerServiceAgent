
from langchain.tools import tool

from src.services.product_service import get_product_by_name
from src.core.tool_result import (
    success,
    not_found,
    failed,
)


@tool
def query_product(product_name: str) -> dict:
    """
    根据商品名称查询商品价格、库存、分类和商品介绍。
    """

    try:
        products = get_product_by_name(product_name)

        # 没有找到商品
        if not products:
            return not_found(
                message=f"没有找到商品：{product_name}"
            )

        # 整理商品数据
        results = []

        for product in products:
            results.append({
                "product_id": product["id"],
                "product_name": product["name"],
                "price": product["price"],
                "stock": product["stock"],
                "category": product.get("category") or "未分类",
                "description": product.get("description") or "暂无介绍",
            })

        return success(
            data=results,
            message=f"商品查询成功，共找到 {len(results)} 件商品。"
        )

    except Exception as e:
        print(
            f"[Product Tool Error] {type(e).__name__}: {e}"
        )

        return failed(
            message="商品查询服务暂时不可用，请稍后重试。"
        )
