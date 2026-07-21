"""测试 rag/retriever.py — 检索和格式化功能。"""

import pytest
from unittest.mock import MagicMock, patch


class TestFormatSearchResults:
    """测试 format_search_results 格式化函数。"""

    def test_formats_results_with_source(self):
        """正确格式化带来源的搜索结果。"""
        with patch("rag.retriever.search_knowledge") as mock_search:
            mock_search.return_value = [
                {
                    "content": "7天无理由退货",
                    "source": "return_policy.txt",
                    "score": 0.85,
                }
            ]

            from rag.retriever import format_search_results

            result = format_search_results("如何退货？")

            assert "return_policy.txt" in result
            assert "7天无理由退货" in result

    def test_formats_multiple_results(self):
        """多条结果用分隔符连接。"""
        with patch("rag.retriever.search_knowledge") as mock_search:
            mock_search.return_value = [
                {"content": "内容A", "source": "faq.txt", "score": 0.9},
                {"content": "内容B", "source": "shipping.txt", "score": 0.7},
            ]

            from rag.retriever import format_search_results

            result = format_search_results("测试")

            assert "内容A" in result
            assert "内容B" in result
            assert "---" in result  # 分隔符

    def test_no_results_returns_friendly_message(self):
        """无结果时返回友好提示。"""
        with patch("rag.retriever.search_knowledge") as mock_search:
            mock_search.return_value = []

            from rag.retriever import format_search_results

            result = format_search_results("完全不相关的问题")

            assert "未在知识库中找到相关信息" in result

    def test_passes_k_parameter(self):
        """正确传递 k 参数给 search_knowledge。"""
        with patch("rag.retriever.search_knowledge") as mock_search:
            mock_search.return_value = []

            from rag.retriever import format_search_results

            format_search_results("测试", k=3)

            mock_search.assert_called_once_with("测试", k=3)


class TestSearchKnowledge:
    """测试 search_knowledge 检索函数。"""

    def test_returns_list_of_dicts(self):
        """返回格式正确的字典列表。"""
        with patch("rag.retriever.Chroma") as mock_chroma, \
             patch("rag.retriever.OllamaEmbeddings"):
            mock_db = MagicMock()
            mock_doc = MagicMock()
            mock_doc.page_content = "退货政策内容"
            mock_doc.metadata = {"source": "return_policy.txt"}

            mock_db.similarity_search_with_score.return_value = [
                (mock_doc, 0.85)
            ]
            mock_chroma.return_value = mock_db

            from rag.retriever import search_knowledge

            results = search_knowledge("退货", k=5)

            assert len(results) == 1
            assert results[0]["content"] == "退货政策内容"
            assert results[0]["source"] == "return_policy.txt"
            assert results[0]["score"] == 0.85

    def test_score_rounded_to_4_decimals(self):
        """分数四舍五入到 4 位小数。"""
        with patch("rag.retriever.Chroma") as mock_chroma, \
             patch("rag.retriever.OllamaEmbeddings"):
            mock_db = MagicMock()
            mock_doc = MagicMock()
            mock_doc.page_content = "test"
            mock_doc.metadata = {"source": "test.txt"}

            mock_db.similarity_search_with_score.return_value = [
                (mock_doc, 0.12345678)
            ]
            mock_chroma.return_value = mock_db

            from rag.retriever import search_knowledge

            results = search_knowledge("test")

            assert results[0]["score"] == 0.1235
