from src.rag.vector_store import get_zilliz_client
from src.rag.bm25_store import HYBRID_COLLECTION_NAME


def bm25_search(
    query: str,
    top_k: int = 3,
) -> list[dict]:
    """使用 BM25 进行中文关键词检索。"""

    if not query or not query.strip():
        raise ValueError("检索问题不能为空")

    print(f"检索问题：{query}")

    # 1. 连接 Zilliz
    client = get_zilliz_client()

    # 2. 加载 Collection
    client.load_collection(
        collection_name=HYBRID_COLLECTION_NAME
    )

    # 3. 执行 BM25 全文检索
    results = client.search(
        collection_name=HYBRID_COLLECTION_NAME,
        data=[query],
        anns_field="sparse",
        limit=top_k,
        search_params={
            "metric_type": "BM25",
            "params": {
                "level": 10
            },
        },
        output_fields=[
            "text",
            "source",
            "file_type",
            "chunk_index",
        ],
    )

    # 4. 整理结果
    retrieved_chunks = []

    for hit in results[0]:
        entity = hit["entity"]

        retrieved_chunks.append({
            "id": hit["id"],
            "score": hit["distance"],
            "text": entity.get("text", ""),
            "source": entity.get("source", ""),
            "file_type": entity.get("file_type", ""),
            "chunk_index": entity.get("chunk_index", -1),
        })

    return retrieved_chunks