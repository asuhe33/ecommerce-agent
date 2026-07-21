# 电商 Agent MVP

本地运行的电商智能助手，覆盖问答、数据分析、客服服务、货品查询、货源查询五大功能。

## 技术栈

- **LLM**: 本地 Ollama (Qwen3.5:9B)
- **Agent 框架**: LangChain (tool-calling agent)
- **向量库**: Chroma + nomic-embed-text embedding
- **数据库**: MySQL
- **UI**: Streamlit

## 功能

| 功能 | 数据来源 | 说明 |
|------|----------|------|
| 问答 | RAG (Chroma) | 产品使用、平台规则、选购建议 |
| 数据分析 | MySQL | 销售统计、热销商品、库存预警 |
| 客服服务 | RAG (Chroma) | 退换货、物流、投诉 |
| 货品查询 | MySQL | 商品名、价格、库存 |
| 货源查询 | MySQL | 供应商信息、供货关系 |

## 快速开始

### 1. 环境准备
```bash
# 安装依赖
pip install -r requirements.txt

# 拉取 Ollama 模型
ollama pull qwen3.5:9B
ollama pull nomic-embed-text
```

### 2. 初始化数据库
```bash
python data/init_db.py
```

### 3. 构建知识库
```bash
python rag/vector_store.py
```

### 4. 启动应用
```bash
streamlit run app.py
```

## 项目结构

```
ecommerce-agent/
├── app.py                    # Streamlit 入口
├── config.py                 # 集中配置
├── requirements.txt
├── data/
│   ├── init_db.py            # 建表 + mock 数据
│   └── knowledge_base/       # RAG 源文档
├── database/
│   └── db_manager.py         # MySQL 连接封装
├── agent/
│   ├── agent_builder.py      # Agent 构建
│   ├── tools.py              # 5 个工具函数
│   └── prompts.py            # 系统提示词
├── rag/
│   ├── vector_store.py       # Chroma 入库
│   └── retriever.py          # 检索函数
└── utils/
    └── ollama_helper.py      # Ollama 连接检查
```
