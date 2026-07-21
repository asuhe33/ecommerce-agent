# 🛒 电商 Agent

> 基于 LangChain + Ollama + MySQL + Chroma 的本地 RAG 智能助手

[![Python](https://img.shields.io/badge/Python-3.12-blue.svg)](https://python.org)
[![LangChain](https://img.shields.io/badge/LangChain-1.3-green.svg)](https://langchain.com)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.59-red.svg)](https://streamlit.io)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 📋 目录

- [项目简介](#项目简介)
- [功能特性](#功能特性)
- [技术架构](#技术架构)
- [快速开始](#快速开始)
- [项目结构](#项目结构)
- [自动化测试](#自动化测试)
- [RAG 知识库扩展](#rag-知识库扩展)
- [部署方案](#部署方案)
- [已知问题](#已知问题)
- [后续规划](#后续规划)
- [相关文档](#相关文档)

---

## 项目简介

电商 Agent 是一个**本地运行**的智能助手系统，利用大语言模型（LLM）和检索增强生成（RAG）技术，为电商场景提供五大核心能力：

- **智能问答**：基于企业知识库回答产品使用、平台规则、选购建议等问题
- **数据分析**：连接 MySQL 数据库，提供销售统计、热销排行、库存预警等分析
- **货品查询**：按名称、分类、关键词搜索商品，返回价格、库存、描述等信息
- **货源查询**：查找供应商信息，支持按供应商名或商品名搜索
- **客服服务**：基于知识库回答退换货、物流、投诉等售后问题

### 核心优势

| 优势 | 说明 |
|------|------|
| 🔒 **数据本地化** | 所有数据和模型均运行在本地，保障数据安全 |
| 🧠 **RAG 增强** | 结合知识库检索，减少幻觉，提高回答准确性 |
| 🔧 **工具调用** | LLM 自动选择合适工具处理用户请求 |
| 📊 **实时数据** | 直接查询 MySQL 获取实时业务数据 |
| 🐳 **容器化部署** | 支持 Docker Compose 一键部署 |

---

## 功能特性

### 五大核心功能

| 功能 | 数据来源 | 典型问题 |
|------|----------|----------|
| 📦 **货品查询** | MySQL | "iPhone 15 多少钱？有货吗？" |
| 🏭 **货源查询** | MySQL | "华为手机的供应商是谁？" |
| 📊 **数据分析** | MySQL | "最近什么商品卖得最好？" |
| ❓ **知识问答** | RAG (Chroma) | "如何注册账号？怎么选手机？" |
| 🎧 **客服服务** | RAG (Chroma) | "退货政策是什么？快递多久到？" |

### 对话示例

```
👤 用户: iPhone 15 多少钱？有货吗？

🤖 助手: 查询到以下商品：

   商品：智能手机 Pro
     分类：电子产品 | 价格：¥4999.00 | 库存：50件
     简介：6.7英寸全面屏，128GB存储

👤 用户: 最近什么商品卖得最好？

🤖 助手: 📊 热销商品排行榜（按销量）：

   1. 智能手机 Pro（电子产品）
      销量：150件 | 销售额：¥749,850.00
   2. 蓝牙耳机（电子产品）
      销量：100件 | 销售额：¥29,900.00

👤 用户: 你们的退货政策是什么？

🤖 助手: 根据我们的退货政策：

   自收到商品之日起7天内，可无理由退货。
   退货商品需保持原包装完好。
```

---

## 技术架构

### 系统架构图

```
┌─────────────────────────────────────────────────────────────────┐
│                         用户交互层                               │
│                     Streamlit Web UI                            │
│                     (http://localhost:8501)                      │
└───────────────────────────────┬─────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                         Agent 层                                │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  LangChain Tool-Calling Agent                            │  │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐      │  │
│  │  │ product_    │  │ supplier_   │ │ data_       │      │  │
│  │  │ lookup      │  │ lookup      │ │ analysis    │      │  │
│  │  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘      │  │
│  │         │                │                │              │  │
│  │         └────────────────┴────────────────┘              │  │
│  │                          │                               │  │
│  │                   ┌──────┴──────┐                        │  │
│  │                   │  ChatOllama │                        │  │
│  │                   │  (LLM)      │                        │  │
│  │                   └─────────────┘                        │  │
│  └──────────────────────────────────────────────────────────┘  │
└───────────────────────────────┬─────────────────────────────────┘
                                │
                ┌───────────────┼───────────────┐
                ▼               ▼               ▼
┌──────────────────┐ ┌──────────────────┐ ┌──────────────────┐
│     MySQL        │ │    Chroma        │ │    Ollama        │
│     (业务数据)    │ │    (向量库)       │ │    (LLM 推理)    │
│                  │ │                  │ │                  │
│  - products      │ │  - 知识文档切片   │ │  - qwen3.5:9b   │
│  - suppliers     │ │  - embeddings    │ │  - nomic-embed   │
│  - customers     │ │  - similarity    │ │                  │
│  - orders        │ │    search        │ │                  │
└──────────────────┘ └──────────────────┘ └──────────────────┘
```

### 技术栈

| 层级 | 技术 | 说明 |
|------|------|------|
| **LLM** | Ollama + Qwen3.5:9B | 本地大语言模型，支持中文 |
| **Embedding** | nomic-embed-text | 文本向量化模型 |
| **Agent 框架** | LangChain 1.3 | Tool-Calling Agent 模式 |
| **向量库** | Chroma | 本地持久化向量存储 |
| **数据库** | MySQL 8.0 | 业务数据存储 |
| **ORM** | SQLAlchemy 2.0 | 数据库连接池 |
| **UI** | Streamlit | Web 交互界面 |
| **部署** | Docker Compose | 容器化编排 |

### 数据流

```
用户提问
   │
   ▼
Streamlit 接收输入
   │
   ▼
Agent 分析问题类型 ──┬──► 需要数据库查询 ──► 调用 product_lookup / supplier_lookup / data_analysis
                    │
                    └──► 需要知识检索 ──► 调用 rag_qa / customer_service
                                                │
                                                ▼
                                          Chroma 相似度检索
                                                │
                                                ▼
                                          返回相关文档片段
                                                │
                                                ▼
                                          LLM 生成最终回答
                                                │
                                                ▼
                                          流式输出到界面
```

---

## 快速开始

### 前置条件

- Python 3.10+
- MySQL 8.0+
- Ollama（[安装指南](https://ollama.com/download)）
- 至少 16GB 可用磁盘空间（模型文件约 7GB）

### 1. 克隆项目

```bash
git clone https://github.com/asuhe33/ecommerce-agent.git
cd ecommerce-agent
```

### 2. 安装依赖

```bash
# 创建虚拟环境（推荐）
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖（国内用户建议使用镜像源）
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### 3. 配置环境变量

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑 .env 文件，填入你的配置
```

`.env` 文件内容：

```env
# Ollama 配置
OLLAMA_BASE_URL=http://localhost:11434
LLM_MODEL=qwen3.5:9b
EMBED_MODEL=nomic-embed-text

# MySQL 配置
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=你的密码
MYSQL_DATABASE=ecommerce

# Chroma 配置
CHROMA_PATH=chroma_db
```

### 4. 拉取 Ollama 模型

```bash
# LLM 模型（6.6GB，首次需要网络）
ollama pull qwen3.5:9b

# Embedding 模型（274MB）
ollama pull nomic-embed-text
```

### 5. 初始化数据库

```bash
# 创建数据库（如果不存在）
mysql -u root -p -e "CREATE DATABASE IF NOT EXISTS ecommerce CHARACTER SET utf8mb4"

# 建表 + 插入 mock 数据
python data/init_db.py

# 如需重新初始化
python data/init_db.py --reset
```

### 6. 构建知识库

```bash
# 向量化知识文档
python rag/vector_store.py

# 如需重新构建
python rag/vector_store.py --reset
```

### 7. 启动应用

```bash
streamlit run app.py
```

浏览器会自动打开 http://localhost:8501

### 8. 命令行测试模式（可选）

```bash
python -m agent.agent_builder
```

---

## 项目结构

```
ecommerce-agent/
├── 📄 配置文件
│   ├── app.py                    # Streamlit 应用入口
│   ├── config.py                 # 集中配置管理（读取 .env）
│   ├── requirements.txt          # Python 依赖
│   ├── .env.example              # 环境变量模板
│   ├── pytest.ini                # 测试配置
│   └── run_tests.bat             # 测试运行脚本（Windows）
│
├── 🐳 Docker 部署
│   ├── Dockerfile                # Docker 镜像构建
│   ├── docker-compose.yml        # 多容器编排
│   ├── docker-entrypoint.sh      # 容器初始化脚本
│   └── .dockerignore             # Docker 构建排除规则
│
├── 📝 文档
│   ├── README.md                 # 项目文档（本文档）
│   └── Suggestion.md             # 优化建议文档
│
├── 📊 数据层
│   ├── data/
│   │   ├── init_db.py            # 数据库初始化（建表 + mock 数据）
│   │   └── knowledge_base/       # RAG 知识库源文档
│   │       ├── faq.txt           # 常见问题
│   │       ├── product_guide.txt # 产品选购指南
│   │       ├── return_policy.txt # 退货政策
│   │       └── shipping_policy.txt # 物流政策
│   │
│   └── database/
│       └── db_manager.py         # MySQL 连接池与查询封装
│
├── 🤖 Agent 层
│   ├── agent/
│   │   ├── agent_builder.py      # Agent 组装（LLM + 工具 + 提示词）
│   │   ├── tools.py              # 5 个工具函数
│   │   └── prompts.py            # 系统提示词
│   │
│   └── rag/
│       ├── vector_store.py       # 向量库管理（加载→切片→向量化→入库）
│       └── retriever.py          # 检索函数（搜索 + 格式化）
│
├── 🔧 工具层
│   └── utils/
│       └── ollama_helper.py      # Ollama 连接检查与模型管理
│
└── 🧪 测试
    └── tests/
        ├── __init__.py
        ├── conftest.py           # 共享 fixtures（mock 数据）
        ├── test_tools.py         # 工具函数测试（19 个用例）
        ├── test_db_manager.py    # 数据库测试（8 个用例）
        ├── test_retriever.py     # 检索测试（6 个用例）
        ├── test_vector_store.py  # 向量库测试（10 个用例）
        ├── test_ollama_helper.py # Ollama 测试（9 个用例）
        └── test_integration.py   # 集成测试（19 个用例）
```

---

## 自动化测试

项目包含 **72 个自动化测试**，覆盖所有核心模块：

| 测试文件 | 测试内容 | 用例数 |
|----------|----------|--------|
| `test_tools.py` | 5 个工具函数的各分支逻辑 | 19 |
| `test_db_manager.py` | 数据库连接管理、只读守卫 | 8 |
| `test_retriever.py` | 检索和格式化功能 | 6 |
| `test_vector_store.py` | 文档加载、切片、ID 生成 | 10 |
| `test_ollama_helper.py` | Ollama 连接检查、模型验证 | 9 |
| `test_integration.py` | 端到端集成测试（需真实环境） | 19 |

### 运行测试

```bash
# 运行全部测试
pytest tests/ -v

# 仅单元测试（无需外部服务，快速验证）
pytest tests/ -v -m "not integration"

# 仅集成测试（需 MySQL + Ollama 环境）
pytest tests/ -v -m integration

# 生成覆盖率报告
pytest tests/ --cov=. --cov-report=html

# Windows 批处理
run_tests.bat
```

---

## RAG 知识库扩展

### 添加新知识文档

1. 将文档转为 `.txt` 格式（UTF-8 编码）
2. 放入 `data/knowledge_base/` 目录
3. 运行 `python rag/vector_store.py`
4. Agent 下次对话即可检索到新知识

### 支持更多文档格式

当前仅支持 `.txt`。如需支持 `.md`、`.docx`、`.pdf`，需修改 `rag/vector_store.py` 中的 `load_documents()` 函数，增加对应格式的加载器（如 `Docx2TxtLoader`、`PyPDFLoader`）。

### 对话历史入库

当前不支持自动保存对话。如需实现：
- 在 `app.py` 中增加"保存对话"按钮
- 将高质量问答对写入 `knowledge_base/`
- 运行 `python rag/vector_store.py` 入库

### 切片策略

当前使用 `RecursiveCharacterTextSplitter`，配置如下：

```python
chunk_size=800      # 每个 chunk 约 800 字符
chunk_overlap=80    # 相邻 chunk 重叠 80 字符
separators=["\n\n", "\n", "。", "！", "？", "；", " ", ""]
```

> 详细扩展指南见 [Suggestion.md](Suggestion.md)

---

## 部署方案

### 方案 A：Docker 容器化部署（推荐）

一键启动所有服务（App + Ollama + MySQL），无需手动配置环境。

#### 前置条件

- 安装 [Docker Desktop](https://www.docker.com/products/docker-compose/)
- 至少 16GB 可用磁盘空间（模型文件约 7GB）

#### 快速启动

```bash
# 1. 克隆项目
git clone https://github.com/asuhe33/ecommerce-agent.git
cd ecommerce-agent

# 2. 启动所有服务
docker-compose up -d

# 3. 首次启动需拉取模型（约 7GB，需要几分钟）
docker-compose exec ollama ollama pull qwen3.5:9b
docker-compose exec ollama ollama pull nomic-embed-text

# 4. 初始化数据库和知识库
docker-compose exec app python data/init_db.py
docker-compose exec app python rag/vector_store.py

# 5. 访问应用
# 浏览器打开 http://localhost:8501
```

#### 常用命令

```bash
# 查看日志
docker-compose logs -f app

# 停止服务
docker-compose down

# 重启应用
docker-compose restart app

# 添加新知识文档
cp 新文档.txt data/knowledge_base/
docker-compose exec app python rag/vector_store.py

# 完全重置（删除所有数据）
docker-compose down -v
```

#### 服务架构

| 服务 | 端口 | 说明 |
|------|------|------|
| app (Streamlit) | 8501 | 电商 Agent 主应用 |
| ollama | 11434 | LLM 推理服务 |
| mysql | 3306 | 数据库服务 |

#### 数据持久化

| 数据 | 存储位置 | 说明 |
|------|----------|------|
| MySQL 数据 | Docker Volume | 容器重启不丢失 |
| Ollama 模型 | Docker Volume | 避免重复下载 |
| Chroma 向量库 | Docker Volume | 知识库持久化 |
| 知识文档 | 本地目录挂载 | 方便添加新文档 |

---

### 方案 B：桌面应用封装（.exe）

将应用打包为 Windows 可执行文件，双击即可运行。

> ⚠️ 注意：Ollama 和 MySQL 仍需单独运行（模型文件 6.6GB 无法打包进 .exe）。

#### 实现方式

使用 `pywebview` + `PyInstaller`：启动 Streamlit 后端 → 在原生浏览器窗口中显示。

#### 步骤

```bash
# 1. 安装打包依赖
pip install pywebview pyinstaller

# 2. 创建桌面入口文件 desktop_app.py

# 3. 打包
pyinstaller --onefile --windowed --name "电商Agent" desktop_app.py
```

#### desktop_app.py 示例

```python
import subprocess, sys, time, threading
import webview

def start_streamlit():
    subprocess.Popen([
        sys.executable, "-m", "streamlit", "run", "app.py",
        "--server.port", "8501",
        "--server.headless", "true",
    ])

if __name__ == "__main__":
    thread = threading.Thread(target=start_streamlit, daemon=True)
    thread.start()
    time.sleep(3)
    webview.create_window("电商智能助手", "http://localhost:8501",
                          width=1200, height=800)
    webview.start()
```

#### 方案对比

| 特性 | Docker 部署 | .exe 桌面应用 |
|------|-------------|---------------|
| 部署复杂度 | 低（一键启动） | 中（需打包） |
| 环境隔离 | ✅ 完全隔离 | ❌ 依赖本机环境 |
| 体积 | 镜像约 2-3GB | 约 1-2GB |
| 启动速度 | 中等（5-10秒） | 较慢（10-20秒） |
| 用户体验 | 浏览器访问 | 原生窗口 |
| 适合场景 | 服务器/团队部署 | 个人单机使用 |
| Ollama/MySQL | 自动包含 | 需单独安装 |

---

## 已知问题

| 问题 | 原因 | 修复方式 |
|------|------|----------|
| 模型名大小写不匹配 | `.env` 写 `qwen3.5:9B`，Ollama 显示 `qwen3.5:9b` | 将 `.env` 改为 `qwen3.5:9b` |
| Windows 下 emoji 报错 | 控制台 GBK 编码不支持 | 已添加 UTF-8 reconfigure |
| LangChain 1.0 导入失败 | 模块路径重构 | 已修复（见 Suggestion.md） |
| 需要手动创建数据库 | `init_db.py` 不自动建库 | 先手动创建或运行 `CREATE DATABASE ecommerce` |

---

## 后续规划

### 短期（1-2 周）

- [ ] 修复模型名大小写不匹配 Bug
- [ ] 合并或区分 `rag_qa` 和 `customer_service` 工具
- [ ] 支持 `.md`、`.docx`、`.pdf` 格式
- [ ] 优化切片策略（按章节切分）

### 中期（1-2 个月）

- [ ] 实现对话历史自动入库
- [ ] 增加文档清洗层（去噪、去重、格式化）
- [ ] 添加知识库管理界面
- [ ] 多轮对话上下文优化

### 长期（3-6 个月）

- [ ] 引入数据中台/ETL 管道处理企业文档
- [ ] 基于用户权限的知识分级检索
- [ ] 知识库版本管理和回滚
- [ ] 多模态知识支持（图片、表格、视频）

> 详细优化建议见 [Suggestion.md](Suggestion.md)

---

## 相关文档

| 文档 | 说明 |
|------|------|
| [Suggestion.md](Suggestion.md) | 优化建议文档（部署问题、代码质量、RAG 扩展、测试建议） |

---

## 许可证

[MIT](LICENSE) © 2024 asuhe33
