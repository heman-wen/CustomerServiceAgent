
import json
import time
import uuid

from langchain_core.messages import (
    SystemMessage,
    HumanMessage,
    AIMessage,
    ToolMessage,
)
from langchain_core.chat_history import InMemoryChatMessageHistory
from pydantic import ValidationError

from src.core.llm import get_llm
from src.core.logger import setup_logger

from src.tools.product_tools import query_product
from src.tools.order_tools import query_order, query_logistics
from src.tools.refund_tools import (
    check_return_window_tool,
    check_refund_eligibility_tool,
)
from src.tools.support_tools import create_support_ticket
from src.tools.knowledge_tools import search_after_sales_knowledge
from src.agent.prompt import get_prompt
from langchain_core.messages.utils import message_chunk_to_message

# 初始化日志
logger = setup_logger(__name__)

SYSTEM_PROMPT = get_prompt()


class CustomerServiceAgent:

    MAX_TOOL_ROUNDS = 5

    VALID_TOOL_STATUSES = {
        "success",
        "not_found",
        "unknown",
        "failed",
    }

    def __init__(self):

        # 初始化模型
        self.llm = get_llm()

        # 注册工具
        self.tools = [
            query_product,
            query_order,
            query_logistics,
            check_refund_eligibility_tool,
            create_support_ticket,
            search_after_sales_knowledge,
            check_return_window_tool,
        ]

        # 将工具绑定到模型
        self.llm_with_tools = self.llm.bind_tools(
            self.tools
        )

        # 建立工具名称与工具对象的映射
        self.tool_map = {
            tool.name: tool
            for tool in self.tools
        }

        # 保存所有会话的记忆
        self.sessions = {}

        logger.info(
            "Agent 初始化成功 | 工具数量=%s",
            len(self.tools),
        )

    def create_session(self):
        """创建一个新的会话。"""

        session_id = str(uuid.uuid4())

        self.sessions[session_id] = InMemoryChatMessageHistory()

        logger.info(
            "创建新会话 | session_id=%s",
            session_id,
        )

        return session_id

    def get_history(self, session_id):
        """获取指定会话的历史记录。"""

        if session_id not in self.sessions:

            self.sessions[session_id] = InMemoryChatMessageHistory()

            logger.info(
                "自动创建会话历史 | session_id=%s",
                session_id,
            )

        return self.sessions[session_id]

    @staticmethod
    def serialize_tool_result(result: dict) -> str:
        """将工具返回的字典转换成 JSON 字符串。"""

        return json.dumps(
            result,
            ensure_ascii=False,
            default=str,
        )

    @classmethod
    def normalize_tool_result(cls, result) -> dict:
        """检查工具返回结果是否符合统一格式。"""

        if not isinstance(result, dict):
            return {
                "success": False,
                "status": "failed",
                "data": None,
                "message": "工具返回结果格式错误。",
            }

        required_fields = {
            "success",
            "status",
            "data",
            "message",
        }

        if not required_fields.issubset(result.keys()):
            return {
                "success": False,
                "status": "failed",
                "data": None,
                "message": "工具返回结果缺少必要字段。",
            }

        status = result["status"]

        if status not in cls.VALID_TOOL_STATUSES:
            return {
                "success": False,
                "status": "failed",
                "data": None,
                "message": "工具返回了无法识别的状态。",
            }

        if not isinstance(result["success"], bool):
            return {
                "success": False,
                "status": "failed",
                "data": None,
                "message": "工具返回结果中的 success 字段格式错误。",
            }

        if not isinstance(result["message"], str):
            return {
                "success": False,
                "status": "failed",
                "data": None,
                "message": "工具返回结果中的 message 字段格式错误。",
            }

        if status == "failed" and result["success"] is not False:
            return {
                "success": False,
                "status": "failed",
                "data": None,
                "message": "工具返回状态与 success 字段不一致。",
            }

        if status != "failed" and result["success"] is not True:
            return {
                "success": False,
                "status": "failed",
                "data": None,
                "message": "工具返回状态与 success 字段不一致。",
            }

        return result

    @staticmethod
    def get_response_text(content) -> str:
        """将模型回答转换为字符串。"""

        if isinstance(content, str):
            return content

        if content is None:
            return ""

        return json.dumps(
            content,
            ensure_ascii=False,
            default=str,
        )

    def chat_stream(self, session_id, user_input):
        """流式处理用户消息，逐块返回 Agent 的最终回答。"""

        history = self.get_history(session_id)

        logger.info(
            "收到用户消息 | session_id=%s | 字符数=%s",
            session_id,
            len(user_input),
        )

        history.add_message(HumanMessage(content=user_input))

        # 最多执行 5 轮工具调用
        for round_index in range(self.MAX_TOOL_ROUNDS):

            current_round = round_index + 1

            messages = [
                SystemMessage(content=SYSTEM_PROMPT),
                *history.messages,
            ]

            # 第一步：流式调用 LLM
            start_time = time.perf_counter()
            full_response = None

            try:
                for chunk in self.llm_with_tools.stream(messages):

                    if full_response is None:
                        full_response = chunk
                    else:
                        full_response += chunk

                    # 将当前文本块返回给 Gradio
                    chunk_text = self.get_response_text(chunk.content)

                    if chunk_text:
                        yield chunk_text

                if full_response is None:
                    raise RuntimeError("LLM 没有返回任何内容。")

                # 将 AIMessageChunk 转换为完整 AIMessage
                response = message_chunk_to_message(full_response)

                elapsed = time.perf_counter() - start_time

                logger.info(
                    "LLM 流式调用成功 | session_id=%s | "
                    "轮次=%s | 耗时=%.2f秒",
                    session_id,
                    current_round,
                    elapsed,
                )

            except Exception as e:

                elapsed = time.perf_counter() - start_time

                logger.exception(
                    "LLM 流式调用失败 | session_id=%s | "
                    "轮次=%s | 耗时=%.2f秒 | 异常类型=%s",
                    session_id,
                    current_round,
                    elapsed,
                    type(e).__name__,
                )

                error_message = "抱歉，客服系统暂时无法响应，请稍后重试。"

                history.add_message(AIMessage(content=error_message))

                yield error_message
                return

            # 保存完整模型响应
            history.add_message(response)

            # 第二步：判断是否需要调用工具
            if not response.tool_calls:

                logger.info(
                    "Agent 完成回答 | session_id=%s | 轮次=%s",
                    session_id,
                    current_round,
                )

                return

            # 第三步：执行工具调用
            for tool_call in response.tool_calls:

                tool_name = tool_call["name"]
                tool_args = tool_call["args"]
                tool_call_id = tool_call["id"]

                logger.info(
                    "开始执行工具 | session_id=%s | 工具=%s | 轮次=%s",
                    session_id,
                    tool_name,
                    current_round,
                )

                tool = self.tool_map.get(tool_name)

                tool_start_time = time.perf_counter()

                # 情况一：工具不存在
                if tool is None:

                    raw_result = {
                        "success": False,
                        "status": "failed",
                        "data": None,
                        "message": f"工具 {tool_name} 不存在或不可用。",
                    }

                    logger.error(
                        "工具不存在 | session_id=%s | 工具=%s",
                        session_id,
                        tool_name,
                    )

                # 情况二：工具存在，尝试执行
                else:

                    try:
                        raw_result = tool.invoke(tool_args)

                    except (
                        ValidationError,
                        TypeError,
                        ValueError,
                    ) as e:

                        raw_result = {
                            "success": False,
                            "status": "failed",
                            "data": None,
                            "message": "工具参数错误，请检查参数后重试。",
                        }

                        logger.warning(
                            "工具参数错误 | session_id=%s | "
                            "工具=%s | 异常类型=%s",
                            session_id,
                            tool_name,
                            type(e).__name__,
                        )

                    except Exception as e:

                        raw_result = {
                            "success": False,
                            "status": "failed",
                            "data": None,
                            "message": "工具执行失败，系统暂时无法完成该操作。",
                        }

                        logger.exception(
                            "工具执行异常 | session_id=%s | "
                            "工具=%s | 异常类型=%s",
                            session_id,
                            tool_name,
                            type(e).__name__,
                        )

                tool_elapsed = time.perf_counter() - tool_start_time

                # 第四步：检查并规范化工具返回结果
                tool_result = self.normalize_tool_result(raw_result)

                if tool_result["status"] == "failed":
                    logger.warning(
                        "工具返回失败 | session_id=%s | 工具=%s",
                        session_id,
                        tool_name,
                    )

                logger.info(
                    "工具执行结束 | session_id=%s | "
                    "工具=%s | 状态=%s | 耗时=%.2f秒",
                    session_id,
                    tool_name,
                    tool_result["status"],
                    tool_elapsed,
                )

                # 第五步：将工具结果返回给模型
                history.add_message(
                    ToolMessage(
                        content=self.serialize_tool_result(tool_result),
                        tool_call_id=tool_call_id,
                    )
                )

        # 第六步：工具调用达到上限，生成最终回答
        logger.warning(
            "达到最大工具调用轮数 | session_id=%s | 最大轮数=%s",
            session_id,
            self.MAX_TOOL_ROUNDS,
        )

        messages = [
            SystemMessage(content=SYSTEM_PROMPT),
            *history.messages,
        ]

        start_time = time.perf_counter()
        full_response = None

        try:
            for chunk in self.llm.stream(messages):

                if full_response is None:
                    full_response = chunk
                else:
                    full_response += chunk

                chunk_text = self.get_response_text(chunk.content)

                if chunk_text:
                    yield chunk_text

            if full_response is None:
                raise RuntimeError("LLM 没有返回最终回答。")

            final_response = message_chunk_to_message(full_response)

            elapsed = time.perf_counter() - start_time

            logger.info(
                "最终回答流式生成成功 | session_id=%s | 耗时=%.2f秒",
                session_id,
                elapsed,
            )

            history.add_message(final_response)

        except Exception as e:

            elapsed = time.perf_counter() - start_time

            logger.exception(
                "最终回答生成失败 | session_id=%s | "
                "耗时=%.2f秒 | 异常类型=%s",
                session_id,
                elapsed,
                type(e).__name__,
            )

            error_message = (
                "抱歉，本次查询涉及的操作较多，"
                "暂时无法生成完整答复，请稍后重试。"
            )

            history.add_message(AIMessage(content=error_message))

            yield error_message


    def chat(self, session_id, user_input):
        """兼容原来的非流式调用方式，例如命令行 Agent。"""

        return "".join(
            self.chat_stream(session_id, user_input)
        )


    
def main():

    agent = CustomerServiceAgent()

    current_session = agent.create_session()

    logger.info("命令行 Agent 已启动")

    print("LangChain 电商客服 Agent 已启动！")
    print(f"当前会话：{current_session}")

    print("\n可用命令：")
    print("/new       创建新会话")
    print("/sessions  查看所有会话")
    print("/use ID    切换会话")
    print("exit       退出程序")

    while True:

        user_input = input("\n用户：").strip()

        if user_input.lower() == "exit":
            logger.info("用户退出命令行 Agent")
            break

        if not user_input:
            continue

        if user_input == "/new":
            current_session = agent.create_session()
            print(f"已创建新会话：{current_session}")
            continue

        if user_input == "/sessions":
            print("\n当前会话列表：")

            for session_id in agent.sessions:
                marker = (
                    "（当前会话）"
                    if session_id == current_session
                    else ""
                )
                print(session_id, marker)

            continue

        if user_input.startswith("/use "):

            target_session = user_input[5:].strip()

            if target_session in agent.sessions:
                current_session = target_session
                print(f"已切换到会话：{current_session}")
            else:
                print("会话不存在，请检查 ID。")

            continue

        try:
            response = agent.chat(
                session_id=current_session,
                user_input=user_input,
            )

            print("\n客服：")
            print(response)

        except Exception as e:
            logger.exception(
                "命令行处理消息失败 | 异常类型=%s",
                type(e).__name__,
            )
            print(
                f"\n发生错误：{type(e).__name__}"
            )


if __name__ == "__main__":
    main()
