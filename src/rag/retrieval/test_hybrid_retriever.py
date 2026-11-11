from src.rag.retrieval.hybrid_retriever import hybrid_search


def main():
    test_queries = [
        "商品签收后几天内可以申请退货？",
        "退款申请需要提供什么信息？",
        "商品出现质量问题，可以退款还是换货？",
        "物流一直没有更新应该怎么办？",
        "商品显示已经签收，但是我没有收到怎么办？",
    ]

    for query in test_queries:
        print("\n" + "=" * 70)
        print("===== 混合检索测试 =====")

        results = hybrid_search(query=query, top_k=3)

        for index, result in enumerate(results, start=1):
            print(f"\n--- 融合结果 {index} ---")
            print(f"RRF 分数：{result['rrf_score']:.6f}")
            print(f"语义相似度：{result['vector_score']}")
            print(f"BM25 分数：{result['bm25_score']}")
            print(f"召回来源：{result['retrieval_sources']}")
            print(f"来源文件：{result['source']}")
            print(f"Chunk 序号：{result['chunk_index']}")
            print(f"文本内容：\n{result['text']}")


if __name__ == "__main__":
    main()