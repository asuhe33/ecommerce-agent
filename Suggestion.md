# 电商 Agent — 优化建议文档

本文档汇总了项目部署、测试和 RAG 知识库扩展过程中的发现与建议。

---

## 一、环境部署问题与修复

### 1.1 pip 安装速度慢

**问题**：默认 PyPI 源下载速度约 50KB/s，安装 LangChain 全家桶 + Chroma + Streamlit 耗时过长。

**解决**：使用国内镜像源（清华源）：

```bash
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

**建议**：在 `requirements.txt` 同目录添加 `pip.conf` 或在全局配置镜像源：

```bash
pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple
```

### 1.2 LangChain 1.0 兼容性

**问题**：项目编写时基于 LangChain 0.x，但安装的 1.0 重构了多个模块路径，导致导入失败。

**已修复的导入变更**：

| 旧导入（0.x） | 新导入（1.0） |
|--------------|--------------|
| `langchain.schema.document.Document` | `langchain_core.documents.Document` |
| `langchain_community.embeddings.OllamaEmbeddings` | `langchain_ollama.OllamaEmbeddings` |
| `langchain_community.chat_models.ChatOllama` | `langchain_ollama.ChatOllama` |
| `langchain.agents.AgentExecutor` | `langchain_classic.agents.AgentExecutor` |
| `langchain.agents.create_tool_calling_agent` | `langchain_classic.agents.create_tool_calling_agent` |

### 1.3 Windows GBK 编码问题

**问题**：Windows 控制台默认 GBK 编码，打印 emoji（✅、❌、⚠️）时报 `UnicodeEncodeError`。

**解决**：在脚本入口处添加：

```python
import sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
```

**已修复文件**：`data/init_db.py`、`rag/vector_store.py`

### 1.4 模型名大小写不匹配（已知 Bug）

**问题**：`.env` 中配置 `LLM_MODEL=qwen3.5:9B`（大写 B），但 `ollama list` 显示 `qwen3.5:9b`（小写 b）。`model_exists()` 是大小写精确匹配，导致 `ensure_models()` 误报模型缺失。

**建议修复**：

- **方案 A**（推荐）：将 `.env` 改为与 `ollama list` 一致：`LLM_MODEL=qwen3.5:9b`
- **方案 B**：修改 `model_exists()` 为大小写不敏感匹配：

```python
def model_exists(model_name: str) -> bool:
    models = list_models()
    name_lower = model_name.lower()
    return any(
        m.lower() == name_lower
        or m.lower().startswith(f"{name_lower}:")
        or name_lower.startswith(f"{m.lower()}:")
        for m in models
    )
```

---

## 二、代码质量问题

### 2.1 rag_qa 与 customer_service 功能重复

**问题**：`agent/tools.py` 中 `rag_qa()` 和 `customer_service()` 两个工具函数完全一致，都调用 `format_search_results(query, k=5)`。

**影响**：LLM 可能随机选择其中一个，无法区分"通用知识问答"和"客服问题"。

**建议**：

- **方案 A**：合并为一个工具 `knowledge_search`，统一处理所有知识类问题
- **方案 B**：保留两个工具但使用不同的 `k` 值或不同的检索策略（如客服工具优先检索退换货、物流类文档）

### 2.2 数据库需手动创建

**问题**：`init_db.py` 假设数据库已存在，但 `mysql_url()` 中指定了数据库名，连接时数据库不存在会报错。

**建议**：在 `init_db.py` 中增加自动创建数据库的逻辑：

```python
from sqlalchemy import create_engine

def create_database():
    """自动创建数据库（如果不存在）。"""
    url = f"mysql+pymysql://{config.MYSQL_USER}:{config.MYSQL_PASSWORD}@{config.MYSQL_HOST}:{config.MYSQL_PORT}/"
    engine = create_engine(url)
    with engine.connect() as conn:
        conn.execute(text(f"CREATE DATABASE IF NOT EXISTS {config.MYSQL_DATABASE} CHARACTER SET utf8mb4"))
    engine.dispose()
```

### 2.3 PYTHONPATH 依赖

**问题**：运行 `init_db.py`、`vector_store.py` 等子目录下的脚本时，需要手动设置 `PYTHONPATH=.`，否则 `from config import config` 会失败。

**建议**：在项目根目录添加 `setup.py` 或使用相对导入，或在 README 中明确说明运行方式。

---

## 三、RAG 知识库扩展指南

### 3.1 添加静态知识文档

**当前支持格式**：仅 `.txt`（UTF-8 编码）

**步骤**：

1. 将文档转为 `.txt` 格式（UTF-8 编码）
2. 放入 `data/knowledge_base/` 目录
3. 运行 `python rag/vector_store.py`
4. 完成！Agent 下次对话即可检索到新知识

**示例**：

```bash
# 添加新产品手册
cp "产品手册V2.txt" data/knowledge_base/
python rag/vector_store.py
```

### 3.2 支持更多文档格式

**当前限制**：`load_documents()` 仅扫描 `*.txt` 文件。

**建议扩展**：增加对 `.md`、`.docx`、`.pdf` 的支持：

```python
# 需要安装：pip install python-docx pypdf langchain-community
from langchain_community.document_loaders import TextLoader, Docx2TxtLoader, PyPDFLoader

def load_documents() -> list:
    documents = []
    loaders = {
        "*.txt": TextLoader,
        "*.md": TextLoader,
        "*.docx": Docx2TxtLoader,
        "*.pdf": PyPDFLoader,
    }
    for pattern, LoaderClass in loaders.items():
        for filepath in KB_DIR.glob(pattern):
            loader = LoaderClass(str(filepath))
            documents.extend(loader.load())
    return documents
```

### 3.3 对话历史存入知识库

**当前状态**：项目**没有**自动保存对话的功能。

**建议实现方案**：

1. 在 `app.py` 中增加"保存此对话"按钮
2. 将高质量问答对自动写入 `knowledge_base/` 目录
3. 定期人工审核后运行 `vector_store.py` 入库

```python
# app.py 中可增加
if st.button("保存此对话到知识库"):
    conversation_text = format_conversation(st.session_state.messages)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    save_path = f"data/knowledge_base/conversation_{timestamp}.txt"
    Path(save_path).write_text(conversation_text, encoding="utf-8")
    st.success("已保存，请运行 python rag/vector_store.py 入库")
```

### 3.4 切片策略优化

**当前策略**：固定 800 字符切片，80 字符重叠。

**问题**：

- 可能把一个完整主题切碎
- 对长文档（产品手册、技术文档）效果不佳
- 无语义理解，检索时可能返回碎片

**建议优化**：

```python
# 按章节/标题切分（Markdown 风格）
splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=100,
    separators=["\n## ", "\n### ", "\n\n", "\n", "。", "！", "？", "；", " ", ""],
)
```

**进阶方案**：

- 短文档（FAQ）：chunk_size=500
- 长文档（手册）：chunk_size=1000-1500
- 添加文档元数据（部门、更新时间、权限级别）

### 3.5 是否需要数据中台清洗？

| 文档状况 | 是否需要清洗 | 建议 |
|----------|-------------|------|
| 结构化文档（FAQ、手册、SOP） | 不需要 | 直接放入 `knowledge_base/` 即可 |
| 半结构化（Word、PDF 扫描件） | 建议清洗 | 去除页眉页脚、乱码、图片、表格 |
| 非结构化（对话记录、会议纪要） | 需要清洗 | 去噪、去重、分段、提取关键信息 |

**企业级 RAG 建议流程**：

```
原始文档 → [清洗] → [格式化] → [切片] → [向量化] → [入库]
              ↑          ↑          ↑
          去噪/去重   转 .txt    按语义分段
```

---

## 四、测试建议

### 4.1 已实现的测试

项目已包含 72 个自动化测试（53 单元测试 + 19 集成测试），覆盖：

- 5 个工具函数的各分支逻辑
- 数据库连接管理和只读守卫
- 向量库文档加载、切片、ID 生成
- Ollama 连接检查和模型验证
- 端到端集成测试（需真实环境）

### 4.2 建议增加的测试

| 测试类型 | 说明 |
|----------|------|
| 性能测试 | 大量文档入库后的检索速度 |
| 准确性测试 | 检索结果与问题的相关性评估 |
| 并发测试 | 多用户同时对话的稳定性 |
| 回归测试 | 更新文档后旧知识是否仍可检索 |

---

## 五、后续优化路线图

### 短期（1-2 周）

- [ ] 修复模型名大小写不匹配 Bug
- [ ] 合并 `rag_qa` 和 `customer_service` 或区分功能
- [ ] 支持 `.md`、`.docx`、`.pdf` 格式
- [ ] 优化切片策略（按章节切分）

### 中期（1-2 个月）

- [ ] 实现对话历史自动入库功能
- [ ] 增加文档清洗层（去噪、去重、格式化）
- [ ] 添加知识库管理界面（上传、删除、更新文档）
- [ ] 支持多轮对话上下文理解优化

### 长期（3-6 个月）

- [ ] 引入数据中台/ETL 管道处理企业文档
- [ ] 实现基于用户权限的知识分级检索
- [ ] 增加知识库版本管理和回滚功能
- [ ] 支持多模态知识（图片、表格、视频描述）
- [ ] 接入企业微信/钉钉等 IM 渠道

---

## 六、项目结构（更新后）

```
ecommerce-agent/
├── app.py                    # Streamlit 入口
├── config.py                 # 集中配置
├── requirements.txt
├── pytest.ini                # 测试配置
├── run_tests.bat             # 测试运行脚本
├── Suggestion.md             # 本文档 — 优化建议
├── data/
│   ├── init_db.py            # 建表 + mock 数据
│   └── knowledge_base/       # RAG 源文档
│       ├── faq.txt
│       ├── product_guide.txt
│       ├── return_policy.txt
│       └── shipping_policy.txt
├── database/
│   └── db_manager.py         # MySQL 连接池
├── agent/
│   ├── agent_builder.py      # Agent 构建
│   ├── tools.py              # 5 个工具函数
│   └── prompts.py            # 系统提示词
├── rag/
│   ├── vector_store.py       # Chroma 入库
│   └── retriever.py          # 检索函数
├── utils/
│   └── ollama_helper.py      # Ollama 连接检查
└── tests/                    # 自动化测试
    ├── __init__.py
    ├── conftest.py           # 共享 fixtures
    ├── test_tools.py         # 工具函数测试
    ├── test_db_manager.py    # 数据库测试
    ├── test_retriever.py     # 检索测试
    ├── test_vector_store.py  # 向量库测试
    ├── test_ollama_helper.py # Ollama 测试
    └── test_integration.py   # 集成测试
```
