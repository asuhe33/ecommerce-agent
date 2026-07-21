#!/bin/bash
# ============================================
# Docker 入口脚本：初始化数据库 + 构建知识库
# ============================================

set -e

echo "=========================================="
echo "   电商 Agent — Docker 初始化"
echo "=========================================="

# 等待 MySQL 就绪
echo "[1/4] 等待 MySQL 就绪..."
for i in $(seq 1 30); do
    if mysqladmin ping -h"$MYSQL_HOST" -u"$MYSQL_USER" -p"$MYSQL_PASSWORD" --silent 2>/dev/null; then
        echo "  ✅ MySQL 已就绪"
        break
    fi
    if [ "$i" -eq 30 ]; then
        echo "  ❌ MySQL 连接超时"
        exit 1
    fi
    sleep 2
done

# 初始化数据库
echo "[2/4] 初始化数据库..."
python data/init_db.py
echo "  ✅ 数据库初始化完成"

# 等待 Ollama 就绪
echo "[3/4] 等待 Ollama 就绪..."
for i in $(seq 1 30); do
    if curl -s "http://ollama:11434/api/tags" > /dev/null 2>&1; then
        echo "  ✅ Ollama 已就绪"
        break
    fi
    if [ "$i" -eq 30 ]; then
        echo "  ⚠️ Ollama 未就绪（首次需拉取模型，可能需要几分钟）"
        break
    fi
    sleep 2
done

# 构建知识库
echo "[4/4] 构建知识库..."
python rag/vector_store.py
echo "  ✅ 知识库构建完成"

echo ""
echo "=========================================="
echo "   初始化完成，启动 Streamlit..."
echo "=========================================="

# 启动 Streamlit
exec streamlit run app.py \
    --server.port=8501 \
    --server.address=0.0.0.0 \
    --server.headless=true \
    --browser.gatherUsageStats=false
