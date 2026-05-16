"""RAG 模块测试 - 验证知识库加载"""

from src.rag.loader import DocumentLoader


def test_loader_reads_products():
    loader = DocumentLoader(chunk_size=2000, chunk_overlap=0)
    docs = loader.load_directory("data/knowledge/products")
    assert len(docs) >= 10, f"Expected >= 10 product doc chunks, got {len(docs)}"


def test_loader_reads_policies():
    loader = DocumentLoader(chunk_size=2000, chunk_overlap=0)
    docs = loader.load_directory("data/knowledge/policies")
    assert len(docs) >= 4, f"Expected >= 4 policy doc chunks, got {len(docs)}"


def test_loader_reads_faq():
    loader = DocumentLoader(chunk_size=2000, chunk_overlap=0)
    docs = loader.load_directory("data/knowledge/faq")
    assert len(docs) >= 5, f"Expected >= 5 FAQ doc chunks, got {len(docs)}"


def test_loader_chunking():
    loader = DocumentLoader(chunk_size=500, chunk_overlap=50)
    docs = loader.load_directory("data/knowledge/products")
    for doc in docs:
        assert len(doc.page_content) <= 600  # 500 + some overlap
        assert "source" in doc.metadata
