from pathlib import Path

from src.rag.ingestion.document_processor import (
    load_markdown,
    split_document,
)
from src.rag.embedding import get_embedding_model
from src.rag.vector_store import get_zilliz_client
from src.rag.bm25_store import HYBRID_COLLECTION_NAME
from src.rag.config import VECTOR_DIMENSION


def ingest_markdown_to_hybrid(file_path: str):
    """将 Markdown 文档写入支持混合检索的 Zilliz Collection。"""

    # 1. 加载文档
    print("===== 第一步：加载文档 =====")

    document = load_markdown(file_path)

    print(f"文档名称：{document.metadata['file_name']}")

    # 2. 切分文档
    print("\n===== 第二步：切分文档 =====")

    nodes = split_document(document)

    if not nodes:
        raise ValueError("文档切分结果为空")

    print(f"生成 Chunk 数量：{len(nodes)}")

    # 3. 生成稠密向量
    print("\n===== 第三步：生成 Embedding =====")

    embed_model = get_embedding_model()

    texts = [
        node.get_content()
        for node in nodes
    ]

    embeddings = embed_model.get_text_embedding_batch(texts)

    if len(embeddings) != len(nodes):
        raise ValueError("Embedding 数量与 Chunk 数量不一致")

    for embedding in embeddings:
        if len(embedding) != VECTOR_DIMENSION:
            raise ValueError(
                f"向量维度错误：期望 {VECTOR_DIMENSION}，"
                f"实际 {len(embedding)}"
            )

    print(f"向量生成成功：{len(embeddings)} 个")
    print(f"向量维度：{len(embeddings[0])}")

    # 4. 组织数据
    print("\n===== 第四步：组织入库数据 =====")

    data = []

    for index, (node, embedding) in enumerate(
        zip(nodes, embeddings)
    ):
        metadata = node.metadata

        data.append({
            "text": node.get_content(),
            "source": metadata.get("file_name", "unknown"),
            "embedding": embedding,

            # 动态字段
            "file_path": metadata.get("file_path", ""),
            "file_type": metadata.get("file_type", ""),
            "chunk_index": index,
        })

    print(f"待写入记录数：{len(data)}")

    # 5. 写入 Zilliz
    print("\n===== 第五步：写入混合检索 Collection =====")

    client = get_zilliz_client()

    # 清理旧数据，避免重复入库
    client.delete(
        collection_name=HYBRID_COLLECTION_NAME,
        filter="id >= 0",
    )

    client.flush(collection_name=HYBRID_COLLECTION_NAME)
    print("旧混合检索知识数据清理完成")

    result = client.insert(
        collection_name=HYBRID_COLLECTION_NAME,
        data=data,
    )

    client.flush(
        collection_name=HYBRID_COLLECTION_NAME
    )

    print("数据写入成功！")
    print(f"实际写入数量：{result['insert_count']}")

    return result


if __name__ == "__main__":
    project_root = Path(__file__).resolve().parents[3]

    markdown_file = (
        project_root
        / "data"
        / "parsed"
        / "after_sales_policy"
        / "extracted"
        / "full.md"
    )

    ingest_markdown_to_hybrid(str(markdown_file))