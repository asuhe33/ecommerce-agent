"""共享 fixtures：mock 外部依赖（DB、Ollama、Chroma）。"""

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# 确保项目根在 Python 路径
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


# ── Mock 数据 ──────────────────────────────────────────────

MOCK_PRODUCTS = [
    {
        "name": "智能手机 Pro",
        "category": "电子产品",
        "price": 4999.00,
        "stock": 50,
        "description": "6.7英寸全面屏，128GB存储",
    },
    {
        "name": "蓝牙耳机",
        "category": "电子产品",
        "price": 299.00,
        "stock": 200,
        "description": "降噪，续航30小时",
    },
]

MOCK_SUPPLIERS = [
    {
        "name": "深圳科技有限公司",
        "contact": "张经理",
        "phone": "13800138000",
        "address": "深圳市南山区科技园",
        "rating": 4.80,
    }
]

MOCK_KB_RESULTS = [
    {
        "content": "自收到商品之日起7天内，可无理由退货。",
        "source": "return_policy.txt",
        "score": 0.85,
    },
    {
        "content": "退货商品需保持原包装完好。",
        "source": "return_policy.txt",
        "score": 0.72,
    },
]


# ── Fixtures ───────────────────────────────────────────────


@pytest.fixture
def mock_db_manager():
    """Mock db_manager，返回预设数据。"""
    with patch("agent.tools.db_manager") as mock:
        yield mock


@pytest.fixture
def mock_retriever():
    """Mock retriever.format_search_results。"""
    with patch("agent.tools.format_search_results") as mock:
        yield mock


@pytest.fixture
def mock_format_search_results():
    """Mock retriever.format_search_results。"""
    with patch("rag.retriever.format_search_results") as mock:
        yield mock


@pytest.fixture
def mock_search_knowledge():
    """Mock retriever.search_knowledge。"""
    with patch("rag.retriever.search_knowledge") as mock:
        yield mock


@pytest.fixture
def mock_requests():
    """Mock requests（用于 ollama_helper）。"""
    with patch("utils.ollama_helper.requests") as mock:
        yield mock


@pytest.fixture
def mock_chroma():
    """Mock Chroma（用于 retriever）。"""
    with patch("rag.retriever.Chroma") as mock:
        yield mock


@pytest.fixture
def mock_ollama_embeddings():
    """Mock OllamaEmbeddings。"""
    with patch("rag.retriever.OllamaEmbeddings") as mock:
        yield mock
