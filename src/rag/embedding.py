
from src.rag.config import (
    MINERU_API_KEY,
    EMBEDDING_MODEL,
)

import os
from dotenv import load_dotenv

from llama_index.embeddings.dashscope import DashScopeEmbedding

load_dotenv()


def get_embedding_model():
    """创建百炼 Embedding 模型。"""

    api_key = os.getenv("DASHSCOPE_API_KEY")

    if not api_key:
        raise ValueError("缺少 DASHSCOPE_API_KEY，请检查 .env")

    return DashScopeEmbedding(
        model_name=EMBEDDING_MODEL,
        api_key=api_key,
    )
