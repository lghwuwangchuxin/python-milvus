from pymilvus import (
    connections,
    utility,
    FieldSchema, CollectionSchema, DataType,
    Collection
)
import random
import traceback
from datetime import datetime

def log_message(message, level="INFO"):
    """统一日志输出格式"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] [{level}] {message}")

# 1. 连接 Milvus
def connect_to_milvus(host="43.255.214.131", port="19530", db_name=None):
    """连接到 Milvus 服务"""
    log_message(f"开始连接 Milvus 服务... host: {host}, port: {port}, db: {db_name}")
    try:
        connections.connect(
            alias="default",
            host=host,
            port=port,
            db_name=db_name
        )
        log_message(f"成功连接到 Milvus (数据库: {db_name or 'default'})")
    except Exception as e:
        log_message(f"连接 Milvus 失败: {e}", "ERROR")
        raise

# 2. 检查数据库支持（兼容旧版本）
def check_database_support():
    """检查是否支持多数据库功能"""
    log_message("检查 Milvus 数据库支持功能...")
    has_list = hasattr(utility, 'list_database')
    has_create = hasattr(utility, 'create_database')
    support = has_list and has_create
    log_message(f"数据库支持检查结果: list_database={has_list}, create_database={has_create}, 支持多数据库={support}")
    return support

# 3. 创建数据库（兼容旧版本）
def create_database(db_name):
    """创建数据库"""
    log_message(f"开始创建数据库: {db_name}")
    if not check_database_support():
        log_message("当前版本不支持多数据库功能，使用默认数据库", "WARNING")
        return False

    try:
        existing_databases = utility.list_database()
        log_message(f"现有数据库列表: {existing_databases}")

        if db_name not in existing_databases:
            utility.create_database(db_name=db_name)
            log_message(f"数据库 '{db_name}' 创建成功")
            return True
        else:
            log_message(f"数据库 '{db_name}' 已存在")
            return True
    except Exception as e:
        log_message(f"创建数据库失败: {e}", "ERROR")
        raise

# 4. 使用数据库（兼容旧版本）
def use_database(db_name):
    """切换到指定数据库"""
    log_message(f"开始切换到数据库: {db_name}")
    if not check_database_support():
        log_message("当前版本不支持多数据库功能，继续使用默认数据库", "WARNING")
        return

    try:
        log_message("断开当前连接...")
        connections.disconnect("default")
        log_message("重新连接到指定数据库...")
        connect_to_milvus("43.255.214.131", "19530", db_name)
        log_message(f"成功切换到数据库 '{db_name}'")
    except Exception as e:
        log_message(f"切换数据库失败: {e}", "ERROR")
        raise

# 5. 创建集合（表）
def create_collection(collection_name):
    """创建集合和字段"""
    log_message(f"开始创建集合: {collection_name}")
    try:
        # 定义字段
        fields = [
            FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),
            FieldSchema(name="user_id", dtype=DataType.INT64),
            FieldSchema(name="name", dtype=DataType.VARCHAR, max_length=256),
            FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=128)
        ]
        log_message("字段定义完成")

        # 创建集合模式
        schema = CollectionSchema(
            fields=fields,
            description="User information collection"
        )
        log_message("集合模式创建完成")

        # 创建集合
        collection = Collection(
            name=collection_name,
            schema=schema,
            using='default'
        )
        log_message(f"集合 '{collection_name}' 创建成功")
        return collection
    except Exception as e:
        log_message(f"创建集合失败: {e}", "ERROR")
        raise

# 6. 创建索引
def create_index(collection):
    """为向量字段创建索引"""
    log_message("开始为向量字段创建索引...")
    try:
        index_params = {
            "index_type": "IVF_FLAT",
            "metric_type": "L2",
            "params": {"nlist": 128}
        }
        log_message(f"索引参数: {index_params}")

        collection.create_index(
            field_name="embedding",
            index_params=index_params
        )
        log_message("向量字段索引创建成功")
    except Exception as e:
        log_message(f"创建索引失败: {e}", "ERROR")
        raise

# 7. 插入数据
def insert_data(collection, num_entities=1000):
    """插入数据"""
    log_message(f"开始插入 {num_entities} 条数据...")
    try:
        # 生成随机数据
        log_message("生成随机数据...")
        user_ids = [random.randint(1, 10000) for _ in range(num_entities)]
        names = [f"user_{i}" for i in range(num_entities)]
        embeddings = [[random.random() for _ in range(128)] for _ in range(num_entities)]
        log_message("数据生成完成")

        # 插入数据
        log_message("开始插入数据...")
        data = [user_ids, names, embeddings]
        result = collection.insert(data)
        log_message("数据插入完成，开始刷新...")
        collection.flush()  # 确保数据写入磁盘
        log_message(f"成功插入 {num_entities} 条实体，插入结果: {result.insert_count} 条记录")
    except Exception as e:
        log_message(f"插入数据失败: {e}", "ERROR")
        raise

# 8. 查询数据
def query_data(collection):
    """查询数据"""
    log_message("开始查询数据...")
    try:
        # 加载集合到内存
        log_message("加载集合到内存...")
        collection.load()
        log_message("集合加载完成")

        # 简单查询
        log_message("执行查询表达式: user_id > 5000")
        result = collection.query(
            expr="user_id > 5000",
            output_fields=["user_id", "name"],
            limit=10
        )
        log_message(f"查询完成，返回 {len(result)} 条结果")
        log_message("查询结果:")
        for i, item in enumerate(result):
            log_message(f"  [{i+1}] {item}")
    except Exception as e:
        log_message(f"查询数据失败: {e}", "ERROR")
        raise

# 9. 向量搜索
def search_data(collection):
    """向量相似度搜索"""
    log_message("开始向量相似度搜索...")
    try:
        # 加载集合到内存
        log_message("加载集合到内存...")
        collection.load()
        log_message("集合加载完成")

        # 生成查询向量
        log_message("生成查询向量...")
        search_vector = [random.random() for _ in range(128)]
        log_message("查询向量生成完成")

        # 执行搜索
        log_message("执行向量搜索...")
        search_params = {
            "metric_type": "L2",
            "params": {"nprobe": 10}
        }
        log_message(f"搜索参数: {search_params}")

        result = collection.search(
            data=[search_vector],
            anns_field="embedding",
            param=search_params,
            limit=5,
            output_fields=["user_id", "name"]
        )
        log_message("向量搜索完成")

        log_message("搜索结果:")
        for i, hits in enumerate(result):
            log_message(f"查询 {i+1} 的结果:")
            for j, hit in enumerate(hits):
                log_message(f"  [{j+1}] id: {hit.id}, distance: {hit.distance}, user_id: {hit.entity.get('user_id')}")
    except Exception as e:
        log_message(f"向量搜索失败: {e}", "ERROR")
        raise

# 10. 删除数据
def delete_data(collection):
    """删除数据"""
    log_message("开始删除数据...")
    try:
        # 删除满足条件的数据
        expr = "user_id < 100"
        log_message(f"删除表达式: {expr}")
        result = collection.delete(expr)
        log_message(f"删除成功，删除表达式: {expr}")
        log_message(f"删除结果: {result}")
    except Exception as e:
        log_message(f"删除数据失败: {e}", "ERROR")
        raise

# 11. 更新数据
def update_data(collection):
    """更新数据（通过删除+插入实现）"""
    log_message("开始更新数据...")
    try:
        # 删除旧数据
        expr = "user_id == 1234"
        log_message(f"删除旧数据，表达式: {expr}")
        collection.delete(expr)

        # 插入新数据
        log_message("插入新数据...")
        user_ids = [1234]
        names = ["updated_user"]
        embeddings = [[random.random() for _ in range(128)]]

        collection.insert([user_ids, names, embeddings])
        collection.flush()
        log_message("数据更新完成 (删除并重新插入)")
    except Exception as e:
        log_message(f"更新数据失败: {e}", "ERROR")
        raise

# 12. 删除集合
def drop_collection(collection_name):
    """删除集合"""
    log_message(f"开始删除集合: {collection_name}")
    try:
        if utility.has_collection(collection_name):
            utility.drop_collection(collection_name)
            log_message(f"集合 '{collection_name}' 删除成功")
        else:
            log_message(f"集合 '{collection_name}' 不存在", "WARNING")
    except Exception as e:
        log_message(f"删除集合失败: {e}", "ERROR")
        raise

# 13. 删除数据库（兼容旧版本）
def drop_database(db_name):
    """删除数据库"""
    log_message(f"开始删除数据库: {db_name}")
    if not check_database_support():
        log_message("当前版本不支持多数据库功能，无法删除数据库", "WARNING")
        return

    try:
        existing_databases = utility.list_database()
        if db_name in existing_databases:
            utility.drop_database(db_name=db_name)
            log_message(f"数据库 '{db_name}' 删除成功")
        else:
            log_message(f"数据库 '{db_name}' 不存在", "WARNING")
    except Exception as e:
        log_message(f"删除数据库失败: {e}", "ERROR")
        raise

# 14. 显示版本信息
def show_version_info():
    """显示版本信息"""
    log_message("获取版本信息...")
    try:
        import pymilvus
        log_message(f"PyMilvus 版本: {pymilvus.__version__}")

        # 检查服务器版本
        server_version = utility.get_server_version()
        log_message(f"Milvus 服务器版本: {server_version}")
    except Exception as e:
        log_message(f"获取版本信息失败: {e}", "ERROR")

# 主函数演示所有操作
def main():
    log_message("开始执行 Milvus 操作演示...")
    db_name = "my_custom_database"  # 使用自定义数据库名称
    collection_name = "user_collection"

    try:
        # 显示版本信息
        show_version_info()

        # 连接到默认数据库以检查数据库支持
        connect_to_milvus()

        # 检查数据库支持
        db_supported = check_database_support()

        if db_supported:
            # 创建自定义数据库
            create_database(db_name)
            # 切换到自定义数据库
            use_database(db_name)
        else:
            log_message("当前版本不支持多数据库功能，使用默认数据库", "WARNING")

        # 创建集合
        collection = create_collection(collection_name)

        # 创建索引
        create_index(collection)

        # 插入数据（减少数量用于测试）
        insert_data(collection, 10)

        # 查询数据
        query_data(collection)

        # 向量搜索
        search_data(collection)

        # 删除数据
        delete_data(collection)

        # 更新数据
        update_data(collection)

        # 显示集合信息
        entity_count = collection.num_entities
        log_message(f"集合信息: {entity_count} 个实体")

    except Exception as e:
        log_message(f"执行过程中发生错误: {e}", "ERROR")
        traceback.print_exc()
    finally:
        # 清理资源（注释掉，避免误删）
        # drop_collection(collection_name)
        # if db_supported:
        #     drop_database(db_name)
        try:
            connections.disconnect("default")
            log_message("已断开 Milvus 连接")
        except Exception as e:
            log_message(f"断开连接时发生错误: {e}", "ERROR")
        log_message("程序执行完成")

if __name__ == "__main__":
    main()
