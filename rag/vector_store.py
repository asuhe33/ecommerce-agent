"""Chroma 向量库管理：文档加载、切片、向量化、入库。

使用方法:
    python rag/vector_store.py          # 将知识库文档入库
    python rag/vector_store.py --reset  # 清空后重新入库
"""

import argparse
import os
from pathlib import Path

from langchain_chroma import Chroma
from langchain_community.embeddings import OllamaEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

from config import config

KB_DIR = Path(__file__).parent.parent / "data" / "knowledge_base"
CHUNK_SIZE = 800
CHUNK_OVERLAP = 80


def get_embedding():
    """创建 Ollama embedding 函数。"""
    return OllamaEmbeddings(
        model=config.EMBED_MODEL,
        base_url=config.OLLAMA_BASE_URL,
    )


def load_documents() -> list:
    """从知识库目录加载所有 .txt 文件。"""
    from langchain.schema.document import Document

    documents = []
    for filepath in KB_DIR.glob("*.txt"):
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
        doc = Document(
            page_content=content,
            metadata={"source": filepath.name, "path": str(filepath)},
        )
        documents.append(doc)
        print(f"[RAG] 已加载: {filepath.name} ({len(content)} 字符)")
    return documents


def split_documents(documents: list) -> list:
    """将文档切分为 chunk。"""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        length_function=len,
        separators=["\n\n", "\n", "。", "！", "？", "；", " ", ""],
    )
    chunks = splitter.split_documents(documents)
    print(f"[RAG] 切分为 {len(chunks)} 个 chunk")
    return chunks


def add_to_chroma(chunks: list, db: Chroma):
    """增量添加 chunk 到 Chroma，跳过已存在的文档。"""
    # 计算 chunk id（基于源文件 + 内容哈希）
    chunks_with_ids = calculate_chunk_ids(chunks)

    existing_items = db.get(include=[])
    existing_ids = set(existing_items["ids"])
    print(f"[RAG] 向量库已有 {len(existing_ids)} 个文档")

    new_chunks = [c for c in chunks_with_ids if c.metadata["id"] not in existing_ids]

    if new_chunks:
        new_ids = [c.metadata["id"] for c in new_chunks]
        db.add_documents(new_chunks, ids=new_ids)
        print(f"[RAG] ✅ 新增 {len(new_chunks)} 个文档到向量库")
    else:
        print("[RAG] ✅ 无新增文档")


def calculate_chunk_ids(chunks: list) -> list:
    """为每个 chunk 生成唯一 ID（源文件名 + 页内索引）。"""
    last_source = None
    current_index = 0
    for chunk in chunks:
        source = chunk.metadata.get("source", "unknown")
        if source == last_source:
            current_index += 1
        else:
            current_index = 0
            last_source = source
        chunk.metadata["id"] = f"{source}:{current_index}"
    return chunks


def main():
    parser = argparse.ArgumentParser(description="构建 Chroma 向量库")
    parser.add_argument("--reset", action="store_true", help="清空后重新入库")
    args = parser.parse_args()

    embedding = get_embedding()

    # 初始化 Chroma
    if args.reset and os.path.exists(config.CHROMA_PATH):
        import shutil
        shutil.rmtree(config.CHROMA_PATH)
        print("[RAG] 已清空旧向量库")

    db = Chroma(
        persist_directory=config.CHROMA_PATH,
        embedding_function=embedding,
    )

    # 加载 → 切分 → 入库
    documents = load_documents()
    if not documents:
        print("[RAG] ⚠️ 知识库目录为空，请先在 data/knowledge_base/ 下放置文档")
        return

    chunks = split_documents(documents)
    add_to_chroma(chunks, db)

    # 验证
    final_count = db.get(include=[])["ids"]
    print(f"[RAG] 🎉 向量库构建完成，共 {len(final_count)} 个文档")


if __name__ == "__main__":
    main()
