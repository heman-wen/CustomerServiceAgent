
from langchain.tools import tool

from src.rag.retrieval.hybrid_retriever import hybrid_search
from src.core.tool_result import (
    success,
    not_found,
    failed,
)


@tool
def search_after_sales_knowledge(query: str) -> dict:
    """
    查询电商平台售后服务知识库。

    当用户询问退货政策、退款规则、商品质量问题、
    物流异常、售后流程等知识性问题时，调用此工具。

    Args:
        query: 用户提出的售后问题。

    Returns:
        统一格式的知识库检索结果。
    """

    try:
        results = hybrid_search(
            query=query,
            top_k=3,
        )

        # 没有检索到相关知识
        if not results:
            return not_found(
                message="知识库中没有检索到相关信息，请勿自行编造售后政策。"
            )

        # 整理检索结果
        knowledge_parts = []

        for index, result in enumerate(results, start=1):
            knowledge_parts.append({
                "index": index,
                "source": result["source"],
                "chunk_index": result["chunk_index"],
                "retrieval_sources": result["retrieval_sources"],
                "text": result["text"],
            })

        return success(
            data=knowledge_parts,
            message=f"知识库检索成功，共检索到 {len(knowledge_parts)} 条相关知识。"
        )

    except Exception as e:
        print(
            f"[Knowledge Tool Error] {type(e).__name__}: {e}"
        )

        return failed(
            message="售后知识库暂时无法使用，请稍后重试。"
        )
