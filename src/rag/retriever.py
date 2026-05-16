"""混合检索器：向量检索 + MMR 增强召回 + 可选 Cross-Encoder 重排序。"""

from langchain_core.documents import Document

from src.rag.vector_store import vector_store_manager


def _get_cross_encoder() -> object | None:
    """懒加载 CrossEncoder 重排序器，不可用时返回 None。"""
    try:
        from langchain_classic.retrievers import ContextualCompressionRetriever
        from langchain_classic.retrievers.document_compressors import (
            CrossEncoderReranker,
        )
        from langchain_community.cross_encoders import HuggingFaceCrossEncoder

        return {
            "class": CrossEncoderReranker,
            "contextual": ContextualCompressionRetriever,
            "model": HuggingFaceCrossEncoder(model_name="BAAI/bge-reranker-v2-m3"),
        }
    except Exception:
        return None


class HybridRetriever:
    """
    混合检索器：向量相似度 + MMR 两路召回 → 合并去重 → Cross-Encoder 重排序（可选）。

    与开发文档 6.2 节一致：混合检索 + 重排序。
    """

    def __init__(self) -> None:
        self.vector_store = vector_store_manager.store
        self._reranker = None

    @property
    def reranker(self) -> object | None:
        if self._reranker is None:
            self._reranker = _get_cross_encoder()
        return self._reranker

    def retrieve(
        self,
        query: str,
        top_k: int = 5,
        filter: dict | None = None,
    ) -> list[Document]:
        # 1. 向量相似度检索（多召回一些候选）
        sim_retriever = self.vector_store.as_retriever(
            search_type="similarity",
            search_kwargs={"k": top_k * 2, "filter": filter},
        )

        # 2. MMR 检索（增加多样性）
        mmr_retriever = self.vector_store.as_retriever(
            search_type="mmr",
            search_kwargs={
                "k": top_k,
                "fetch_k": top_k * 3,
                "filter": filter,
            },
        )

        # 3. 合并去重
        vector_docs = list(sim_retriever.invoke(query))
        mmr_docs = list(mmr_retriever.invoke(query))
        all_docs = self._deduplicate(vector_docs + mmr_docs)

        # 4. Cross-Encoder 重排序（可用时）
        reranker = self.reranker
        if reranker is not None and len(all_docs) > 0:
            try:
                reranker_cls = reranker["class"]
                compressor = reranker_cls(
                    model=reranker["model"],
                    top_n=min(top_k, len(all_docs)),
                )
                compression_retriever = reranker["contextual"](
                    base_compressor=compressor,
                    base_retriever=sim_retriever,
                )
                reranked = compression_retriever.compress_documents(
                    documents=all_docs[: top_k * 2],
                    query=query,
                )
                return reranked[:top_k]
            except Exception:
                pass

        # 降级：返回合并去重后的结果
        return all_docs[:top_k]

    def _deduplicate(self, docs: list[Document]) -> list[Document]:
        seen: set[str] = set()
        unique: list[Document] = []
        for doc in docs:
            key = doc.page_content
            if key not in seen:
                seen.add(key)
                unique.append(doc)
        return unique
