from src.tools.knowledge_tools import search_after_sales_knowledge


def main():
    queries = [
        "商品签收后几天内可以申请退货？",
        "商品有质量问题应该怎么办？",
        "物流一直没有更新应该如何处理？",
    ]

    for query in queries:
        print("\n" + "=" * 60)
        print(f"用户问题：{query}")

        result = search_after_sales_knowledge.invoke({
            "query": query
        })

        print("\n知识库返回结果：")
        print(result)


if __name__ == "__main__":
    main()