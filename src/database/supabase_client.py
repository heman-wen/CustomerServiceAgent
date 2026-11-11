import os
from functools import lru_cache

from dotenv import load_dotenv
from supabase import Client, create_client

from src.core.logger import setup_logger


load_dotenv()

logger = setup_logger(__name__)


@lru_cache(maxsize=1)
def get_supabase() -> Client:
    """
    创建并缓存 Supabase 客户端。

    整个 Python 进程复用同一个客户端，
    避免每次查询都重新建立连接。
    """

    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")

    if not url:
        raise ValueError("缺少 SUPABASE_URL，请检查 .env")

    if not key:
        raise ValueError("缺少 SUPABASE_KEY，请检查 .env")

    try:
        client = create_client(url, key)

        logger.info("Supabase 客户端初始化成功")

        return client

    except Exception:
        logger.exception("Supabase 客户端初始化失败")
        raise