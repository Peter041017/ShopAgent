from pathlib import Path

from langchain_chroma import Chroma

from src.config.settings import settings
from src.rag.embeddings import get_embeddings


class VectorStoreManager:
    def __init__(self) -> None:
        self._store: Chroma | None = None

    @property
    def store(self) -> Chroma:
        if self._store is None:
            Path(settings.CHROMA_PERSIST_DIR).mkdir(parents=True, exist_ok=True)
            self._store = Chroma(
                collection_name=settings.CHROMA_COLLECTION_NAME,
                embedding_function=get_embeddings(),
                persist_directory=settings.CHROMA_PERSIST_DIR,
            )
        return self._store

    def add_documents(self, docs: list, batch_size: int = 100) -> None:
        for i in range(0, len(docs), batch_size):
            batch = docs[i : i + batch_size]
            self.store.add_documents(batch)

    def search(
        self,
        query: str,
        k: int = 5,
        filter: dict | None = None,
    ) -> list:
        return self.store.similarity_search_with_score(query, k=k, filter=filter)


vector_store_manager = VectorStoreManager()
