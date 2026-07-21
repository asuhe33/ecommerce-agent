"""测试 rag/vector_store.py — 文档加载、切分、ID 生成。"""

import pytest
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

from langchain_core.documents import Document


class TestLoadDocuments:
    """测试 load_documents 文档加载。"""

    def test_loads_txt_files_from_kb_dir(self):
        """从知识库目录加载所有 .txt 文件。"""
        with tempfile.TemporaryDirectory() as tmpdir:
            kb_dir = Path(tmpdir)
            (kb_dir / "faq.txt").write_text("常见问题内容", encoding="utf-8")
            (kb_dir / "guide.txt").write_text("购买指南内容", encoding="utf-8")

            with patch("rag.vector_store.KB_DIR", kb_dir):
                from rag.vector_store import load_documents

                docs = load_documents()

            assert len(docs) == 2
            contents = {d.page_content for d in docs}
            assert "常见问题内容" in contents
            assert "购买指南内容" in contents

    def test_documents_have_metadata(self):
        """加载的文档包含正确的 metadata。"""
        with tempfile.TemporaryDirectory() as tmpdir:
            kb_dir = Path(tmpdir)
            (kb_dir / "test.txt").write_text("测试内容", encoding="utf-8")

            with patch("rag.vector_store.KB_DIR", kb_dir):
                from rag.vector_store import load_documents

                docs = load_documents()

            assert docs[0].metadata["source"] == "test.txt"
            assert "test.txt" in docs[0].metadata["path"]

    def test_empty_dir_returns_empty_list(self):
        """空目录返回空列表。"""
        with tempfile.TemporaryDirectory() as tmpdir:
            kb_dir = Path(tmpdir)

            with patch("rag.vector_store.KB_DIR", kb_dir):
                from rag.vector_store import load_documents

                docs = load_documents()

            assert docs == []


class TestSplitDocuments:
    """测试 split_documents 文档切分。"""

    def test_splits_long_document(self):
        """长文档被切分为多个 chunk。"""
        long_text = "这是一段测试内容。" * 200  # 长文本
        docs = [Document(page_content=long_text, metadata={"source": "test.txt"})]

        from rag.vector_store import split_documents

        chunks = split_documents(docs)

        assert len(chunks) > 1

    def test_short_document_stays_single_chunk(self):
        """短文档保持为 1 个 chunk。"""
        short_text = "短内容"
        docs = [Document(page_content=short_text, metadata={"source": "test.txt"})]

        from rag.vector_store import split_documents

        chunks = split_documents(docs)

        assert len(chunks) == 1
        assert chunks[0].page_content == short_text

    def test_chunks_have_metadata(self):
        """切分后的 chunk 保留源文档 metadata。"""
        text = "内容" * 500
        docs = [Document(page_content=text, metadata={"source": "faq.txt"})]

        from rag.vector_store import split_documents

        chunks = split_documents(docs)

        for chunk in chunks:
            assert "source" in chunk.metadata
            assert chunk.metadata["source"] == "faq.txt"


class TestCalculateChunkIds:
    """测试 calculate_chunk_ids ID 生成。"""

    def test_generates_sequential_ids(self):
        """同一文件的 chunk 生成顺序 ID。"""
        docs = [
            Document(page_content="内容1", metadata={"source": "faq.txt"}),
            Document(page_content="内容2", metadata={"source": "faq.txt"}),
            Document(page_content="内容3", metadata={"source": "faq.txt"}),
        ]

        from rag.vector_store import calculate_chunk_ids

        result = calculate_chunk_ids(docs)

        assert result[0].metadata["id"] == "faq.txt:0"
        assert result[1].metadata["id"] == "faq.txt:1"
        assert result[2].metadata["id"] == "faq.txt:2"

    def test_resets_index_for_new_source(self):
        """不同文件的索引重置。"""
        docs = [
            Document(page_content="内容1", metadata={"source": "faq.txt"}),
            Document(page_content="内容2", metadata={"source": "guide.txt"}),
        ]

        from rag.vector_store import calculate_chunk_ids

        result = calculate_chunk_ids(docs)

        assert result[0].metadata["id"] == "faq.txt:0"
        assert result[1].metadata["id"] == "guide.txt:0"

    def test_ids_are_unique(self):
        """生成的 ID 唯一。"""
        docs = [
            Document(page_content=f"内容{i}", metadata={"source": "test.txt"})
            for i in range(5)
        ]

        from rag.vector_store import calculate_chunk_ids

        result = calculate_chunk_ids(docs)

        ids = [d.metadata["id"] for d in result]
        assert len(ids) == len(set(ids))  # 全部唯一
