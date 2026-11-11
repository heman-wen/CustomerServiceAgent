from src.rag.retrieval.bm25_retriever import bm25_search


def main():
    test_queries = [
        "签收后7天退货",
        "商品质量问题退款换货",
        "物流长时间没有更新",
    ]

    for query in test_queries:
        print("\n" + "=" * 50)
        print("===== BM25 关键词检索测试 =====")

        results = bm25_search(
            query=query,
            top_k=3,
        )

        print(f"\n检索结果数量：{len(results)}")

        for index, result in enumerate(results, start=1):
            print(f"\n--- 结果 {index} ---")
            print(f"BM25 分数：{result['score']:.4f}")
            print(f"来源文件：{result['source']}")
            print(f"Chunk 序号：{result['chunk_index']}")
            print(f"文本内容：\n{result['text']}")


if __name__ == "__main__":
    main()