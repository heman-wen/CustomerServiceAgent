import os

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

load_dotenv()


def get_llm():
    """创建配置了超时和重试机制的 Qwen 大模型实例。"""

    api_key = os.getenv("DASHSCOPE_API_KEY")
    base_url = os.getenv("DASHSCOPE_BASE_URL")
    model_name = os.getenv("QWEN_MODEL", "qwen-plus")

    if not api_key:
        raise ValueError("缺少 DASHSCOPE_API_KEY")

    if not base_url:
        raise ValueError("缺少 DASHSCOPE_BASE_URL")

    return ChatOpenAI(
        model=model_name,
        api_key=api_key,
        base_url=base_url,
        temperature=0,

        # 请求超时时间：60 秒
        timeout=60,

        # 失败后最多重试 3 次
        max_retries=3,
    )