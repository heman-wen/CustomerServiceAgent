
import gradio as gr

from src.agent.basic_agent import CustomerServiceAgent


# 初始化 Agent。
# 整个网页应用只创建一个 Agent 实例，
# 不要在每次用户发送消息时重新创建 Agent。
agent = CustomerServiceAgent()


def create_new_session():
    """创建一个新的聊天会话。"""
    session_id = agent.create_session()
    return [], "", session_id



def chat(message, history, session_id):
    """流式接收 Agent 回答并更新 Gradio 聊天记录。"""

    if not message or not message.strip():
        yield history or [], ""
        return

    updated_history = list(history or [])

    # 先显示用户消息和一个空的客服消息
    updated_history.append({
        "role": "user",
        "content": message,
    })

    updated_history.append({
        "role": "assistant",
        "content": "",
    })

    # 立即更新界面，同时清空输入框
    yield updated_history, ""

    try:
        # 逐块接收 Agent 的回答
        for chunk in agent.chat_stream(session_id, message):

            updated_history[-1]["content"] += chunk

            # 每收到一个文本块，就更新一次聊天窗口
            yield updated_history, ""

    except Exception as e:

        print(
            f"网页聊天发生异常：{type(e).__name__}: {e}"
        )

        updated_history[-1]["content"] = (
            "抱歉，客服系统暂时遇到问题，请稍后重试。"
        )

        yield updated_history, ""


# 创建初始会话
initial_session_id = agent.create_session()


# 构建网页界面
with gr.Blocks(title="智能电商客服 Agent") as demo:

    gr.Markdown(
        """
        # 智能电商客服 Agent

        基于 LangChain + Qwen + RAG 的智能客服系统
        """
    )

    session_state = gr.State(initial_session_id)

    chatbot = gr.Chatbot(
        label="客服对话",
        height=550,
    )

    with gr.Row():
        message_input = gr.Textbox(
            placeholder="请输入你的问题，例如：AirPods Pro 2 多少钱？",
            show_label=False,
            scale=8,
            lines=2,
            max_lines=5,
        )

        send_button = gr.Button(
            "发送",
            variant="primary",
            scale=1,
        )

    new_session_button = gr.Button("新建会话")

    # 按 Enter 发送消息
    message_input.submit(
        fn=chat,
        inputs=[message_input, chatbot, session_state],
        outputs=[chatbot, message_input],
    )

    # 点击发送按钮
    send_button.click(
        fn=chat,
        inputs=[message_input, chatbot, session_state],
        outputs=[chatbot, message_input],
    )

    # 创建新会话
    new_session_button.click(
        fn=create_new_session,
        inputs=[],
        outputs=[chatbot, message_input, session_state],
    )


if __name__ == "__main__":
    demo.launch(
        server_name="127.0.0.1",
        server_port=7777,
        inbrowser=True,
    )
