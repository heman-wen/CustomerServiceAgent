from src.rag.retrieval.vector_retriever import vector_search
from src.rag.retrieval.bm25_retriever import bm25_search
from src.rag.retrieval.reranker import rerank_documents

def get_chunk_key(result: dict) -> tuple:
    """生成 Chunk 的稳定标识。"""

    source = result.get("source", "")
    chunk_index = result.get("chunk_index", -1)

    # 优先使用文档来源和 Chunk 序号
    if source and chunk_index != -1:
        return source, chunk_index

    # 缺少元数据时，使用文本作为备用标识
    return result.get("text", ""),


def reciprocal_rank_fusion(
    vector_results: list[dict],
    bm25_results: list[dict],
    top_k: int = 5,
    rrf_k: int = 60,
) -> list[dict]:
    """使用 RRF 算法融合向量检索和 BM25 检索结果。"""

    fused_results = {}

    retrieval_groups = [
        ("vector", vector_results),
        ("bm25", bm25_results),
    ]

    for retrieval_name, results in retrieval_groups:

        # 记录当前检索路线已经处理过的 Chunk
        seen_keys = set()

        for rank, result in enumerate(results, start=1):

            key = get_chunk_key(result)

            # 同一路检索中，重复 Chunk 只处理一次
            if key in seen_keys:
                continue

            seen_keys.add(key)

            if key not in fused_results:
                fused_results[key] = {
                    **result,
                    "rrf_score": 0.0,
                    "retrieval_sources": [],
                    "vector_score": None,
                    "bm25_score": None,
                }

            item = fused_results[key]

            # RRF 分数累计
            item["rrf_score"] += 1 / (rrf_k + rank)

            # 记录召回来源，避免重复
            if retrieval_name not in item["retrieval_sources"]:
                item["retrieval_sources"].append(retrieval_name)

            if retrieval_name == "vector":
                item["vector_score"] = result.get("score")

            elif retrieval_name == "bm25":
                item["bm25_score"] = result.get("score")

    sorted_results = sorted(
        fused_results.values(),
        key=lambda item: item["rrf_score"],
        reverse=True,
    )

    return sorted_results[:top_k]


def hybrid_search(
    query: str,
    top_k: int = 3,
    candidate_k: int = 10,
) -> list[dict]:
    """执行混合召回、RRF 融合和 Reranker 重排序。"""

    if not query or not query.strip():
        raise ValueError("检索问题不能为空")

    print(f"\n用户问题：{query}")

    # 1. 语义向量检索
    print("\n===== 第一步：语义检索 =====")

    vector_results = vector_search(
        query=query,
        top_k=candidate_k,
    )

    print(f"语义检索结果：{len(vector_results)} 条")

    # 2. BM25 关键词检索
    print("\n===== 第二步：BM25 检索 =====")

    bm25_results = bm25_search(
        query=query,
        top_k=candidate_k,
    )

    print(f"BM25 检索结果：{len(bm25_results)} 条")

    # 3. RRF 融合
    print("\n===== 第三步：RRF 结果融合 =====")

    fused_results = reciprocal_rank_fusion(
        vector_results=vector_results,
        bm25_results=bm25_results,
        top_k=candidate_k,
    )

    print(f"RRF 融合结果：{len(fused_results)} 条")

    if not fused_results:
        return []

    # 4. Reranker 模型重排序
    print("\n===== 第四步：Reranker 重排序 =====")

    reranked_results = rerank_documents(
        query=query,
        documents=fused_results,
        top_n=top_k,
    )

    print(f"Reranker 最终结果：{len(reranked_results)} 条")

    return reranked_results
