"""检索函数：供 Agent 的 RAG 工具调用。"""

from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings

from config import config


def get_db() -> Chroma:
    """获取 Chroma 实例。"""
    embedding = OllamaEmbeddings(
        model=config.EMBED_MODEL,
        base_url=config.OLLAMA_BASE_URL,
    )
    return Chroma(
        persist_directory=config.CHROMA_PATH,
        embedding_function=embedding,
    )


def search_knowledge(query: str, k: int = 5) -> list[dict]:
    """搜索知识库，返回相关文档片段。

    Returns:
        list of {"content": str, "source": str, "score": float}
    """
    db = get_db()
    results = db.similarity_search_with_score(query, k=k)

    documents = []
    for doc, score in results:
        documents.append({
            "content": doc.page_content,
            "source": doc.metadata.get("source", "unknown"),
            "score": round(score, 4),
        })
    return documents


def format_search_results(query: str, k: int = 5) -> str:
    """搜索知识库并格式化为可读文本（供 LLM 工具直接返回）。"""
    results = search_knowledge(query, k=k)
    if not results:
        return "未在知识库中找到相关信息。"

    parts = []
    for i, r in enumerate(results, 1):
        parts.append(f"[来源: {r['source']}]\n{r['content']}")
    return "\n\n---\n\n".join(parts)
