from pathlib import Path

from langchain_community.document_loaders import CSVLoader, TextLoader
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter


class DocumentLoader:
    """加载各种格式的电商知识文档"""

    def __init__(
        self,
        chunk_size: int = 800,
        chunk_overlap: int = 120,
    ):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=["\n## ", "\n### ", "\n\n", "\n", "。", ".", " ", ""],
            length_function=len,
        )

    def _load_json_file(self, file_path: Path) -> list[Document]:
        import json

        raw = file_path.read_text(encoding="utf-8")
        data = json.loads(raw)
        if isinstance(data, list):
            parts = [json.dumps(item, ensure_ascii=False) for item in data]
            content = "\n\n".join(parts)
        else:
            content = json.dumps(data, ensure_ascii=False, indent=2)
        return [
            Document(
                page_content=content,
                metadata={"source": str(file_path), "category": file_path.parent.name},
            )
        ]

    def load_directory(self, path: str) -> list[Document]:
        docs: list[Document] = []
        root = Path(path)
        if not root.exists():
            return []
        for file_path in root.rglob("*"):
            if not file_path.is_file():
                continue
            suffix = file_path.suffix.lower()
            try:
                if suffix in (".txt", ".md"):
                    loader = TextLoader(str(file_path), encoding="utf-8")
                    loaded = loader.load()
                elif suffix == ".csv":
                    loader = CSVLoader(str(file_path), encoding="utf-8")
                    loaded = loader.load()
                elif suffix == ".json":
                    loaded = self._load_json_file(file_path)
                else:
                    continue
                for doc in loaded:
                    doc.metadata.setdefault("source", str(file_path))
                    doc.metadata.setdefault("category", file_path.parent.name)
                docs.extend(loaded)
            except Exception:
                continue
        if not docs:
            return []
        return self.text_splitter.split_documents(docs)

    def load_faq(self, faq_data: list[dict]) -> list[Document]:
        """加载 FAQ 数据，以 Q 为检索单元"""
        out: list[Document] = []
        for item in faq_data:
            out.append(
                Document(
                    page_content=f"Q: {item['question']}\nA: {item['answer']}",
                    metadata={"type": "faq", "tags": item.get("tags", [])},
                )
            )
        return out
