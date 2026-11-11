from pymilvus import MilvusClient, DataType

from src.rag.config import (
    ZILLIZ_CLOUD_URI,
    ZILLIZ_CLOUD_TOKEN,
    ZILLIZ_COLLECTION_NAME,
    VECTOR_DIMENSION,
)


def get_zilliz_client():
    """创建 Zilliz Cloud 客户端。"""

    if not ZILLIZ_CLOUD_URI:
        raise ValueError("缺少 ZILLIZ_CLOUD_URI，请检查 .env")

    if not ZILLIZ_CLOUD_TOKEN:
        raise ValueError("缺少 ZILLIZ_CLOUD_TOKEN，请检查 .env")

    client = MilvusClient(
        uri=ZILLIZ_CLOUD_URI,
        token=ZILLIZ_CLOUD_TOKEN,
    )

    return client


def create_knowledge_collection():
    """创建客服知识库 Collection。"""

    client = get_zilliz_client()

    # 避免重复创建
    if client.has_collection(ZILLIZ_COLLECTION_NAME):
        print(f"Collection 已存在：{ZILLIZ_COLLECTION_NAME}")
        return client

    # 1. 定义 Collection Schema
    schema = MilvusClient.create_schema(
        auto_id=True,
        enable_dynamic_field=True,
    )

    # 主键：自动生成
    schema.add_field(
        field_name="id",
        datatype=DataType.INT64,
        is_primary=True,
        auto_id=True,
    )

    # 文本内容
    schema.add_field(
        field_name="text",
        datatype=DataType.VARCHAR,
        max_length=65535,
    )

    # 原始文档名称
    schema.add_field(
        field_name="source",
        datatype=DataType.VARCHAR,
        max_length=512,
    )

    # 文本向量
    schema.add_field(
        field_name="embedding",
        datatype=DataType.FLOAT_VECTOR,
        dim=VECTOR_DIMENSION,
    )

    # 2. 创建向量索引
    index_params = client.prepare_index_params()

    index_params.add_index(
        field_name="embedding",
        index_type="AUTOINDEX",
        metric_type="COSINE",
    )

    # 3. 创建 Collection
    client.create_collection(
        collection_name=ZILLIZ_COLLECTION_NAME,
        schema=schema,
        index_params=index_params,
    )

    print(f"Collection 创建成功：{ZILLIZ_COLLECTION_NAME}")

    return client