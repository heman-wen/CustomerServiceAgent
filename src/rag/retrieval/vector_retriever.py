from src.rag.embedding import get_embedding_model
from src.rag.vector_store import get_zilliz_client
from src.rag.config import (
    ZILLIZ_COLLECTION_NAME,
    VECTOR_DIMENSION,
)


def vector_search(
    query: str,
    top_k: int = 3,
) -> list[dict]:
    """根据用户问题进行语义向量检索。"""

    if not query or not query.strip():
        raise ValueError("检索问题不能为空")

    print(f"检索问题：{query}")

    # 1. 将用户问题转换成向量
    embed_model = get_embedding_model()

    query_embedding = embed_model.get_query_embedding(query)

    if len(query_embedding) != VECTOR_DIMENSION:
        raise ValueError(
            f"查询向量维度错误：期望 {VECTOR_DIMENSION}，"
            f"实际 {len(query_embedding)}"
        )

    # 2. 连接 Zilliz
    client = get_zilliz_client()

    # 3. 执行向量搜索
    results = client.search(
        collection_name=ZILLIZ_COLLECTION_NAME,
        data=[query_embedding],
        anns_field="embedding",
        limit=top_k,
        search_params={
            "metric_type": "COSINE",
            "params": {},
        },
        output_fields=[
            "text",
            "source",
            "file_type",
            "chunk_index",
        ],
    )

    # 4. 整理检索结果
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