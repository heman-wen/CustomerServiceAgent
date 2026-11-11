import re
from pathlib import Path

from llama_index.core import Document
from llama_index.core.node_parser import SentenceSplitter

from src.rag.config import CHUNK_SIZE, CHUNK_OVERLAP


def clean_markdown(text: str) -> str:
    """清洗 MinerU 输出的 Markdown 文本。"""

    text = re.sub(r"\\([#*_`])", r"\1", text)
    text = text.replace("\r\n", "\n")
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()


def load_markdown(file_path: str) -> Document:
    """加载 Markdown 文件。"""

    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"文件不存在：{path}")

    text = path.read_text(encoding="utf-8")
    text = clean_markdown(text)

    if not text:
        raise ValueError("文档内容为空")

    return Document(
        text=text,
        metadata={
            "file_name": path.name,
            "file_path": str(path),
            "file_type": "markdown",
        },
    )


def split_document(document: Document):
    """
    先按照 Markdown 二级标题切分，
    再使用 SentenceSplitter 对过长的部分进行二次切分。
    """

    text = document.text

    # 按 Markdown 二级标题切分，保留标题本身
    sections = re.split(r"(?=^##\s+)", text, flags=re.MULTILINE)

    splitter = SentenceSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
    )

    nodes = []

    for section in sections:
        section = section.strip()

        if not section:
            continue
        # 过滤只有 Markdown 标题、没有实际正文的内容
        content_without_titles = re.sub(
            r"^#{1,6}\s+.*$",
            "",
            section,
            flags=re.MULTILINE,
        ).strip()

        if not content_without_titles:
            continue
        # 提取当前章节标题
        title_match = re.match(r"^##\s+(.+)", section)
        section_title = title_match.group(1).strip() if title_match else "文档概述"

        section_document = Document(
            text=section,
            metadata={
                **document.metadata,
                "section_title": section_title,
            },
        )

        section_nodes = splitter.get_nodes_from_documents(
            [section_document]
        )

        nodes.extend(section_nodes)

    # 为每个 Chunk 添加编号
    for index, node in enumerate(nodes):
        node.metadata["chunk_index"] = index

    return nodes