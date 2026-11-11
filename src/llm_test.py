import os

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage


# 读取 .env 文件
load_dotenv()


def get_llm():
    """创建 Qwen 模型实例"""

    api_key = os.getenv("DASHSCOPE_API_KEY")
    base_url = os.getenv("DASHSCOPE_BASE_URL")
    model_name = os.getenv("QWEN_MODEL")

    if not api_key:
        raise ValueError("没有找到 DASHSCOPE_API_KEY，请检查 .env 文件")

    if not base_url:
        raise ValueError("没有找到 DASHSCOPE_BASE_URL，请检查 .env 文件")

    llm = ChatOpenAI(
        model=model_name,
        api_key=api_key,
        base_url=base_url,
        temperature=0,
    )

    return llm


def main():
    llm = get_llm()

    messages = [
        SystemMessage(
            content="你是一名专业的电商客服助手，请用中文回答问题。"
        ),
        HumanMessage(
            content="你好，请简单介绍一下你自己。"
        ),
    ]

    response = llm.invoke(messages)

    print("\n========== Qwen 回复 ==========\n")
    print(response.content)
    print("\n===============================\n")


if __name__ == "__main__":
    main()