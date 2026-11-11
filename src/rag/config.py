
import os

from dotenv import load_dotenv

load_dotenv()

MINERU_API_KEY = os.getenv("MINERU_API_KEY")

MINERU_BASE_URL = "https://mineru.net/api/v4"

# 解析模型：vlm 对复杂版面、表格等场景更合适
MINERU_MODEL_VERSION = "vlm"

# 轮询配置
MINERU_POLL_INTERVAL = 3
MINERU_MAX_WAIT_SECONDS = 1800

# LlamaIndex 文本向量模型
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL")

# 文本切分参数
CHUNK_SIZE = 500
CHUNK_OVERLAP = 80

# Zilliz Cloud 配置
ZILLIZ_CLOUD_URI = os.getenv("ZILLIZ_CLOUD_URI")
ZILLIZ_CLOUD_TOKEN = os.getenv("ZILLIZ_CLOUD_TOKEN")

# Zilliz Collection 配置
ZILLIZ_COLLECTION_NAME = "customer_service_knowledge"
VECTOR_DIMENSION = 1024