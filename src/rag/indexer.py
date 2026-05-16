"""供应用内调用的索引构建逻辑（脚本入口见 scripts/build_index.py）。"""

from src.rag.loader import DocumentLoader
from src.rag.vector_store import vector_store_manager


def build_default_index() -> int:
    loader = DocumentLoader(chunk_size=800, chunk_overlap=120)
    product_docs = loader.load_directory("data/knowledge/products")
    policy_docs = loader.load_directory("data/knowledge/policies")
    faq_docs = loader.load_directory("data/knowledge/faq")
    all_docs = product_docs + policy_docs + faq_docs
    if all_docs:
        vector_store_manager.add_documents(all_docs)
    return len(all_docs)
