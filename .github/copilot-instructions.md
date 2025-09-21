# Copilot Instructions for python-milvus

## 项目概览
- 本项目为 Milvus（向量数据库）Python 客户端的演示与工具集，核心文件为 `base-milvus.py`，涵盖了数据库/集合的创建、数据插入、查询、向量搜索、索引管理等全流程。
- 主要依赖 [PyMilvus](https://pymilvus.io/)，通过 `pymilvus` 包与 Milvus 服务通信。

## 结构与主要模式
- 所有操作均以函数方式封装，主流程在 `main()` 中串联演示。
- 日志输出统一使用 `log_message()`，便于调试和追踪。
- 兼容 Milvus 多数据库功能（如不支持则自动降级为默认数据库）。
- 集合（Collection）结构固定：包含 `id`（自增主键）、`user_id`、`name`、`embedding`（128维向量）。
- 数据插入、查询、向量搜索、删除、更新等均有独立函数，便于复用和扩展。

## 关键开发工作流
- **依赖安装**：需先安装 `pymilvus`，如：`pip install pymilvus`
- **运行演示**：直接运行 `python base-milvus.py`，会自动连接远程 Milvus 服务并演示全流程。
- **Milvus 服务地址**：默认连接 `43.255.214.131:19530`，如需更改请修改 `connect_to_milvus()` 的参数。
- **调试建议**：可单独调用各函数进行分步调试，或修改 `main()` 以定制流程。
- **异常处理**：所有操作均有异常捕获和日志输出，便于定位问题。

## 项目约定与注意事项
- **日志格式**：所有日志均带时间戳和级别，便于排查。
- **多数据库兼容**：如目标 Milvus 版本不支持多数据库，相关操作会自动降级。
- **集合/数据库清理**：`main()` 中的清理操作（删除集合/数据库）默认注释，避免误删数据。
- **外部依赖**：仅依赖 `pymilvus`，无其他第三方包。
- **数据生成**：插入/搜索数据均为随机生成，便于测试。

## 典型用法示例
- 创建集合：`create_collection('my_collection')`
- 插入数据：`insert_data(collection, 100)`
- 查询数据：`query_data(collection)`
- 向量搜索：`search_data(collection)`

## 参考文件
- 主要逻辑均在 `base-milvus.py`，无其他核心模块。

---
如需扩展功能或集成到更大项目，建议保持函数式封装和统一日志风格。
