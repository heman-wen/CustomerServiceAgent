from pymilvus import (
    DataType,
    Function,
    FunctionType,
)

from src.rag.vector_store import get_zilliz_client


# 新的混合检索 Collection
HYBRID_COLLECTION_NAME = "customer_service_knowledge_hybrid"


def create_hybrid_collection():
    """创建支持向量检索和 BM25 检索的 Collection。"""

    client = get_zilliz_client()

    # 避免重复创建
    if client.has_collection(HYBRID_COLLECTION_NAME):
        print(
            f"Collection 已存在：{HYBRID_COLLECTION_NAME}"
        )
        return client

    # 1. 创建 Schema
    schema = client.create_schema(
        auto_id=True,
        enable_dynamic_field=True,
    )

    # 主键
    schema.add_field(
        field_name="id",
        datatype=DataType.INT64,
        is_primary=True,
        auto_id=True,
    )

    # 文本字段，启用中文分词
    schema.add_field(
        field_name="text",
        datatype=DataType.VARCHAR,
        max_length=65535,
        enable_analyzer=True,
        analyzer_params={
            "type": "chinese"
        },
    )

    # 来源文件
    schema.add_field(
        field_name="source",
        datatype=DataType.VARCHAR,
        max_length=512,
    )

    # 稠密向量：语义检索
    schema.add_field(
        field_name="embedding",
        datatype=DataType.FLOAT_VECTOR,
        dim=1024,
    )

    # 稀疏向量：BM25 关键词检索
    schema.add_field(
        field_name="sparse",
        datatype=DataType.SPARSE_FLOAT_VECTOR,
    )

    # 2. 添加 BM25 Function
    bm25_function = Function(
        name="text_bm25",
        input_field_names=["text"],
        output_field_names=["sparse"],
        function_type=FunctionType.BM25,
    )

    schema.add_function(bm25_function)

    # 3. 创建索引
    index_params = client.prepare_index_params()

    # 稠密向量索引
    index_params.add_index(
        field_name="embedding",
        index_type="AUTOINDEX",
        metric_type="COSINE",
    )

    # BM25 稀疏向量索引
    index_params.add_index(
        field_name="sparse",
        index_type="AUTOINDEX",
        metric_type="BM25",
    )

    # 4. 创建 Collection
    client.create_collection(
        collection_name=HYBRID_COLLECTION_NAME,
        schema=schema,
        index_params=index_params,
    )

    print(
        f"混合检索 Collection 创建成功："
        f"{HYBRID_COLLECTION_NAME}"
    )

    return client