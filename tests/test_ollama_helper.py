"""测试 utils/ollama_helper.py — Ollama 连接检查。"""

import pytest
from unittest.mock import MagicMock, patch

import requests as real_requests


class TestCheckOllamaRunning:
    """测试 check_ollama_running。"""

    def test_returns_true_when_ollama_running(self):
        """Ollama 运行时返回 True。"""
        with patch("utils.ollama_helper.requests") as mock_req:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_req.get.return_value = mock_response

            from utils.ollama_helper import check_ollama_running

            assert check_ollama_running() is True

    def test_returns_false_when_ollama_down(self):
        """Ollama 不可用时返回 False。"""
        with patch("utils.ollama_helper.requests.get") as mock_get:
            mock_get.side_effect = real_requests.ConnectionError("refused")

            from utils.ollama_helper import check_ollama_running

            assert check_ollama_running() is False


class TestListModels:
    """测试 list_models。"""

    def test_returns_model_names(self):
        """正确解析并返回模型名称列表。"""
        with patch("utils.ollama_helper.requests") as mock_req:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "models": [
                    {"name": "qwen3.5:9b"},
                    {"name": "nomic-embed-text:latest"},
                ]
            }
            mock_req.get.return_value = mock_response

            from utils.ollama_helper import list_models

            models = list_models()

            assert "qwen3.5:9b" in models
            assert "nomic-embed-text:latest" in models

    def test_returns_empty_list_on_error(self):
        """请求失败返回空列表。"""
        with patch("utils.ollama_helper.requests") as mock_req:
            mock_req.get.side_effect = Exception("Error")

            from utils.ollama_helper import list_models

            assert list_models() == []


class TestModelExists:
    """测试 model_exists。"""

    def test_model_exists_with_tag(self):
        """带标签的模型名能正确匹配。"""
        with patch("utils.ollama_helper.list_models") as mock_list:
            mock_list.return_value = ["qwen3.5:9b"]

            from utils.ollama_helper import model_exists

            assert model_exists("qwen3.5:9b") is True

    def test_model_not_exists(self):
        """不存在的模型返回 False。"""
        with patch("utils.ollama_helper.list_models") as mock_list:
            mock_list.return_value = ["qwen3.5:9b"]

            from utils.ollama_helper import model_exists

            assert model_exists("llama3") is False

    def test_model_exists_without_tag_matches_latest(self):
        """不带标签的模型名能匹配 :latest。"""
        with patch("utils.ollama_helper.list_models") as mock_list:
            mock_list.return_value = ["nomic-embed-text:latest"]

            from utils.ollama_helper import model_exists

            assert model_exists("nomic-embed-text") is True


class TestEnsureModels:
    """测试 ensure_models — 验证两个模型都存在。"""

    def test_returns_true_when_both_models_exist(self):
        """两个模型都存在时返回 True。"""
        with patch("utils.ollama_helper.list_models") as mock_list:
            # 注意：config 中 LLM_MODEL 是 "qwen3.5:9B"（大写 B）
            mock_list.return_value = [
                "qwen3.5:9B",
                "nomic-embed-text:latest",
            ]

            from utils.ollama_helper import ensure_models

            assert ensure_models() is True

    def test_returns_false_when_model_missing(self):
        """缺少任一模型时返回 False。"""
        with patch("utils.ollama_helper.list_models") as mock_list:
            mock_list.return_value = ["qwen3.5:9b"]  # 缺少 embedding 模型

            from utils.ollama_helper import ensure_models

            assert ensure_models() is False

    def test_returns_false_when_ollama_down(self):
        """Ollama 未运行时返回 False。"""
        with patch("utils.ollama_helper.check_ollama_running") as mock_check:
            mock_check.return_value = False

            from utils.ollama_helper import ensure_models

            assert ensure_models() is False
