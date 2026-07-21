"""集中配置管理，从 .env 读取所有连接参数。"""

import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    # Ollama
    OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    LLM_MODEL = os.getenv("LLM_MODEL", "qwen3.5:9B")
    EMBED_MODEL = os.getenv("EMBED_MODEL", "nomic-embed-text")

    # MySQL
    MYSQL_HOST = os.getenv("MYSQL_HOST", "localhost")
    MYSQL_PORT = int(os.getenv("MYSQL_PORT", 3306))
    MYSQL_USER = os.getenv("MYSQL_USER", "root")
    MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "")
    MYSQL_DATABASE = os.getenv("MYSQL_DATABASE", "ecommerce")

    # Chroma
    CHROMA_PATH = os.getenv("CHROMA_PATH", "chroma_db")

    @classmethod
    def mysql_url(cls) -> str:
        return (
            f"mysql+pymysql://{cls.MYSQL_USER}:{cls.MYSQL_PASSWORD}"
            f"@{cls.MYSQL_HOST}:{cls.MYSQL_PORT}/{cls.MYSQL_DATABASE}"
        )


config = Config()
