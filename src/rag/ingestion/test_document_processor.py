from pathlib import Path


from src.rag.ingestion.document_processor import (
load_markdown,
split_document,
)
from src.rag.embedding import get_embedding_model

def main():
    project_root = Path(__file__).resolve().parents[3]

    markdown_file = (
    project_root
    / "data"
    / "parsed"
    / "after_sales_policy"
    / "extracted"
    / "full.md"
    )

    print("===== 第一步：加载文档 =====")

    document = load_markdown(str(markdown_file))

    print(f"文档名称：{document.metadata['file_name']}")
    print(f"文档长度：{len(document.text)} 字符")

    print("\n===== 第二步：切分文档 =====")

    nodes = split_document(document)

    print(f"切分完成，共生成 {len(nodes)} 个 Chunk")

    for index, node in enumerate(nodes, start=1):
        print(f"\n--- Chunk {index} ---")
        print(node.get_content())

        print("\n===== 第三步：测试 Embedding =====")

        embed_model = get_embedding_model()

        first_chunk = nodes[0].get_content()
        embedding = embed_model.get_text_embedding(first_chunk)

        print(f"向量生成成功！")
        print(f"向量维度：{len(embedding)}")
        print(f"向量前 5 个值：{embedding[:5]}")

if __name__ == "__main__":
    main()
