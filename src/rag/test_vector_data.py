from src.rag.vector_store import (
    get_zilliz_client,
    ZILLIZ_COLLECTION_NAME,
)


def main():
    print("===== Zilliz 数据验证 =====")

    client = get_zilliz_client()

    # 查询 Collection 中的数据
    results = client.query(
        collection_name=ZILLIZ_COLLECTION_NAME,
        filter="",
        output_fields=[
            "text",
            "source",
            "file_path",
            "file_type",
            "chunk_index",
        ],
        limit=10,
    )

    print(f"\n查询到记录数：{len(results)}")

    for index, record in enumerate(results, start=1):
        print(f"\n===== 第 {index} 条记录 =====")

        print(f"主键 ID：{record.get('id')}")
        print(f"来源文件：{record.get('source')}")
        print(f"文件类型：{record.get('file_type')}")
        print(f"Chunk 序号：{record.get('chunk_index')}")
        print(f"文本内容：\n{record.get('text')}")

    if not results:
        print("没有查询到数据，请检查 Collection 和入库过程。")
        return

    print("\nZilliz 数据验证通过！")


if __name__ == "__main__":
    main()