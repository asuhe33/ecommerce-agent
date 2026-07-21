"""Ollama 连接检查和模型管理工具。"""

import sys

# 修复 Windows GBK 编码
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

import requests

from config import config


def check_ollama_running() -> bool:
    """检查 Ollama 服务是否在运行。"""
    try:
        resp = requests.get(f"{config.OLLAMA_BASE_URL}/api/tags", timeout=5)
        return resp.status_code == 200
    except requests.ConnectionError:
        return False


def list_models() -> list[str]:
    """列出本地已安装的 Ollama 模型。"""
    try:
        resp = requests.get(f"{config.OLLAMA_BASE_URL}/api/tags", timeout=5)
        resp.raise_for_status()
        data = resp.json()
        return [m["name"] for m in data.get("models", [])]
    except Exception as e:
        print(f"[Ollama] 获取模型列表失败: {e}")
        return []


def model_exists(model_name: str) -> bool:
    """检查指定模型是否已安装。"""
    models = list_models()
    # 支持带 tag 和不带 tag 的匹配
    return any(
        m == model_name or m.startswith(f"{model_name}:") or model_name.startswith(f"{m}:")
        for m in models
    )


def pull_model(model_name: str) -> bool:
    """拉取模型（需要网络）。"""
    print(f"[Ollama] 正在拉取模型 {model_name}...")
    try:
        resp = requests.post(
            f"{config.OLLAMA_BASE_URL}/api/pull",
            json={"name": model_name},
            stream=True,
            timeout=600,
        )
        for line in resp.iter_lines():
            if line:
                print(f"  {line.decode('utf-8')}")
        return True
    except Exception as e:
        print(f"[Ollama] 拉取失败: {e}")
        return False


def ensure_models():
    """确保所需模型都已安装，缺少的给出提示。"""
    if not check_ollama_running():
        print("[Ollama] ❌ Ollama 服务未运行，请先启动 Ollama")
        return False

    required = [config.LLM_MODEL, config.EMBED_MODEL]
    models = list_models()
    print(f"[Ollama] 已安装模型: {models}")

    missing = []
    for m in required:
        if not model_exists(m):
            missing.append(m)

    if missing:
        print(f"[Ollama] ⚠️ 缺少模型: {missing}")
        print(f"[Ollama] 请运行: ollama pull {' '.join(missing)}")
        return False

    print("[Ollama] ✅ 所需模型已就绪")
    return True


if __name__ == "__main__":
    ensure_models()
