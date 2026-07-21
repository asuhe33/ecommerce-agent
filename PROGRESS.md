# 电商 Agent MVP - 开发进度跟踪

## Day 1：基础搭建（数据库 + 知识库）

- [x] 项目初始化：目录结构、requirements.txt、.env、config.py、.gitignore、README.md
- [ ] 安装依赖 + 配置 Ollama（`ollama pull nomic-embed-text`）
- [x] 编写 config.py：集中读取 .env 配置
- [x] 编写 database/db_manager.py：MySQL 连接池
- [x] 编写 data/init_db.py：建表 + 生成 mock 数据（50商品/10供应商/30客户/200订单）
- [x] 编写 4 篇知识文档（faq/return/shipping/product_guide）
- [x] 编写 rag/vector_store.py：文档切片 + 向量化 + Chroma 入库
- [x] 编写 rag/retriever.py：检索函数
- [ ] 验证：init_db.py 建表成功，Chroma 能返回相关片段（需要用户配置 MySQL + 安装依赖后执行）

**Day 1 完成时间**: ____________

---

## Day 2：Agent 核心（工具 + Agent 组装）

- [x] 编写 utils/ollama_helper.py：Ollama 连接检查 + 模型拉取
- [ ] 编写 agent/tools.py：5 个工具函数（product_lookup, supplier_lookup, data_analysis, rag_qa, customer_service）
- [ ] 编写 agent/prompts.py：系统提示词（角色定义 + 工具选择指南）
- [ ] 编写 agent/agent_builder.py：LangChain Agent 组装
- [ ] CLI 测试循环：命令行交互测试每个工具
- [ ] 修复工具调用问题（如需启用 ReAct fallback）

**Day 2 完成时间**: ____________

---

## Day 3：界面 + 集成 + 收尾

- [ ] 编写 app.py：Streamlit 聊天界面（对话历史 + 流式输出）
- [ ] Agent ↔ Streamlit 集成，处理会话状态
- [ ] 端到端测试：5 类场景各测几轮
- [ ] 修复测试中发现的问题
- [ ] 更新 README.md + 代码整理

**Day 3 完成时间**: ____________

---

## Git 提交记录

| 日期 | 提交信息 | 说明 |
|------|----------|------|
| Day 1 | `chore: project setup + database + knowledge base` | 基础搭建 |
| Day 2 | `feat: agent core with 5 tools + Ollama integration` | Agent 核心 |
| Day 3 | `feat: Streamlit UI + end-to-end integration` | 界面集成 |
