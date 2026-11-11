from src.core.logger import setup_logger

logger = setup_logger()

logger.debug("这是一条 DEBUG 日志")
logger.info("Agent 启动成功")
logger.warning("这是一条 WARNING 日志")
logger.error("这是一条 ERROR 日志")

print("日志测试完成！")