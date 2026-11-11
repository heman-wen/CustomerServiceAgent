
from src.services.product_service import (
    get_product_by_name,
    get_product_by_id,
)


def main():
    print("===== 测试：按名称查询 =====")
    products = get_product_by_name("AirPods")

    for product in products:
        print(
            f"商品 ID：{product['id']}\n"
            f"商品名称：{product['name']}\n"
            f"价格：{product['price']} 元\n"
            f"库存：{product['stock']}\n"
        )

    print("===== 测试：按 ID 查询 =====")
    product = get_product_by_id("P002")

    if product:
        print(f"查询成功：{product['name']}，价格：{product['price']} 元")
    else:
        print("没有找到该商品")


if __name__ == "__main__":
    main()
