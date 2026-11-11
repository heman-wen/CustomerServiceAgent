from src.rag.bm25_store import (
    create_hybrid_collection,
    HYBRID_COLLECTION_NAME,
)


def main():
    print("===== 创建混合检索 Collection =====")

    client = create_hybrid_collection()

    print("\n===== 验证 Collection =====")

    exists = client.has_collection(
        HYBRID_COLLECTION_NAME
    )

    print(f"Collection 是否存在：{exists}")

    if exists:
        print("混合检索 Collection 创建成功！")


if __name__ == "__main__":
    main()