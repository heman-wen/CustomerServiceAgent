
from src.database.supabase_client import get_supabase


def main():

    print("正在连接 Supabase...")

    supabase = get_supabase()

    # 查询商品表
    response = (
        supabase
        .table("products")
        .select("id, name, price, stock")
        .execute()
    )

    products = response.data

    print("\nSupabase 连接成功！")
    print(f"查询到 {len(products)} 个商品：")

    for product in products:
        print(
            f"{product['id']} | "
            f"{product['name']} | "
            f"{product['price']} 元 | "
            f"库存：{product['stock']}"
        )


if __name__ == "__main__":
    main()
