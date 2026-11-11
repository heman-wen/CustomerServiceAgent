from src.rag.retrieval.vector_retriever import vector_search


def main():
    test_queries = [
        "商品签收后几天内可以申请退货？",
        "商品有质量问题应该怎么处理？",
        "物流一直没有更新怎么办？",
    ]

    for query in test_queries:
        print("\n" + "=" * 50)
        print("===== 语义检索测试 =====")

        results = vector_search(
            query=query,
            top_k=3,
        )

        print(f"\n检索结果数量：{len(results)}")

        for index, result in enumerate(results, start=1):
            print(f"\n--- 结果 {index} ---")
            print(f"相似度分数：{result['score']:.4f}")
            print(f"来源文件：{result['source']}")
            print(f"Chunk 序号：{result['chunk_index']}")
            print(f"文本内容：\n{result['text']}")


if __name__ == "__main__":
    main()