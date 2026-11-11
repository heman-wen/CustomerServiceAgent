
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path


# 项目根目录
BASE_DIR = Path(__file__).resolve().parents[2]

# 日志目录
LOG_DIR = BASE_DIR / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)

# 日志文件
LOG_FILE = LOG_DIR / "app.log"


def setup_logger(name: str = "customer_service") -> logging.Logger:
    """初始化项目统一日志系统。"""

    logger = logging.getLogger(name)

    # 防止重复添加 Handler
    if logger.handlers:
        return logger

    logger.setLevel(logging.INFO)

    # 日志格式
    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # 控制台日志
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)

    # 文件日志：5MB 自动轮转，保留 3 个备份
    file_handler = RotatingFileHandler(
        LOG_FILE,
        maxBytes=5 * 1024 * 1024,
        backupCount=3,
        encoding="utf-8",
    )
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger
