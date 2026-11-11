
import os

import requests
from dotenv import load_dotenv

from src.core.logger import setup_logger

load_dotenv()

logger = setup_logger(__name__)


def rerank_documents(
    query: str,
    documents: list[dict],
    top_n: int = 3,
    score_threshold: float | None = None,
) -> list[dict]:
    """
    调用 Reranker 模型重新排序，并过滤低相关性文档。
    """

    if not query or not query.strip():
        raise ValueError("Reranker 查询问题不能为空")

    if not documents:
        return []

    api_url = os.getenv("RERANK_API_URL")
    api_key = os.getenv("DASHSCOPE_API_KEY")
    model = os.getenv("RERANK_MODEL", "qwen3-rerank")

    if not api_url:
        raise ValueError("缺少 RERANK_API_URL")

    if not api_key:
        raise ValueError("缺少 DASHSCOPE_API_KEY")

    if score_threshold is None:
        score_threshold = float(
            os.getenv("RERANK_SCORE_THRESHOLD", "0.5")
        )

    if not 0 <= score_threshold <= 1:
        raise ValueError("RERANK_SCORE_THRESHOLD 必须在 0 到 1 之间")

    texts = [
        item.get("text", "")
        for item in documents
    ]

    payload = {
        "model": model,
        "input": {
            "query": query,
            "documents": texts,
        },
        "parameters": {
            "top_n": min(len(texts), len(texts)),
        },
    }

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    try:
        response = requests.post(
            api_url,
            headers=headers,
            json=payload,
            timeout=30,
        )

        response.raise_for_status()

        result = response.json()

        ranked_results = result.get(
            "output", {}
        ).get("results", [])

        reranked_documents = []

        for item in ranked_results:
            index = item.get("index")

            if not isinstance(index, int):
                continue

            if index < 0 or index >= len(documents):
                continue

            score = item.get("relevance_score")

            if not isinstance(score, (int, float)):
                continue

            # 过滤低相关性 Chunk
            if score < score_threshold:
                continue

            document = documents[index].copy()
            document["rerank_score"] = score

            reranked_documents.append(document)

        # 保留过滤后的 Top N
        reranked_documents = reranked_documents[:top_n]

        logger.info(
            "Reranker 完成：候选 %s 条，阈值 %.2f，过滤后 %s 条",
            len(documents),
            score_threshold,
            len(reranked_documents),
        )

        return reranked_documents

    except Exception:
        logger.exception("Reranker 模型调用失败")
        raise
