
from src.agent.basic_agent import CustomerServiceAgent


def main():
    agent = CustomerServiceAgent()
    session_id = agent.create_session()

    test_questions = [
        "AirPods Pro 2 多少钱？还有库存吗？",

        "帮我查询一下订单 ORD202611080001 的状态。",

        "我的订单 ORD202611080001 现在物流到哪里了？",

        "我的订单 ORD202611080001 有质量问题，可以申请退款吗？",

        "我的 AirPods 有杂音，请帮我联系人工客服，"
        "创建一个高优先级工单，关联订单 ORD202611080001。",
    ]

    for index, question in enumerate(test_questions, start=1):
        print("\n" + "=" * 60)
        print(f"测试场景 {index}")
        print(f"用户：{question}")
        print("-" * 60)

        answer = agent.chat(session_id, question)

        print(f"客服：{answer}")


if __name__ == "__main__":
    main()
