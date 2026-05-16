"""RAG 检索效果评估脚本"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.rag.retriever import HybridRetriever


def evaluate() -> None:
    retriever = HybridRetriever()
    test_queries = [
        ("iPhone 16 Pro 电池容量是多少", "product"),
        ("退货需要什么条件", "policy"),
        ("你们支持花呗分期吗", "faq"),
    ]

    for query, expected_category in test_queries:
        docs = retriever.retrieve(query, top_k=3)
        print(f"\n查询: {query} (期望类目: {expected_category})")
        for i, doc in enumerate(docs):
            cat = doc.metadata.get("category", "?")
            preview = doc.page_content[:80].replace("\n", " ")
            print(f"  #{i + 1} [{cat}] {preview}...")


if __name__ == "__main__":
    evaluate()
