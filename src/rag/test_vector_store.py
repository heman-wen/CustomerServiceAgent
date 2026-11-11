from src.rag.vector_store import create_knowledge_collection


def main():
    print("===== Zilliz Cloud 连接测试 =====")

    client = create_knowledge_collection()

    print("\n===== Collection 信息 =====")

    collection_name = "customer_service_knowledge"

    print(f"Collection 是否存在：{client.has_collection(collection_name)}")

    print("\nZilliz Cloud 测试完成！")


if __name__ == "__main__":
    main()