"""RAG 检索节点 — 知识库 + fallback 到原始文档。"""

import re
from pathlib import Path

from src.agent.state import AgentState
from src.rag.loader import DocumentLoader
from src.rag.retriever import HybridRetriever
from src.utils.logger import get_logger

logger = get_logger(__name__)

# 全局缓存：已在内存中的原始文档，避免每次查询都重复读文件
_loaded_docs: list[dict] | None = None

# 可被显式赋值为 True（如 build_index 脚本设此标志）
_INDEX_READY = False


def mark_index_ready() -> None:
    """标记 Chroma 索引已就绪，跳过 fallback 加载（性能优化）。"""
    global _INDEX_READY
    _INDEX_READY = True


def _get_project_root() -> Path:
    """获取项目根目录（相对于本文件的上级目录的上级目录的上级目录）。"""
    return Path(__file__).resolve().parent.parent.parent.parent


def _load_knowledge_docs() -> list[dict]:
    """直接读取 data/knowledge 下的 markdown 文档，返回序列化结果。"""
    global _loaded_docs
    if _loaded_docs is not None:
        return _loaded_docs

    loader = DocumentLoader(chunk_size=1000, chunk_overlap=200)
    all_docs: list[dict] = []
    project_root = _get_project_root()

    for subdir in ("products", "policies", "faq"):
        path = project_root / "data" / "knowledge" / subdir
        if not path.exists():
            continue
        try:
            docs = loader.load_directory(path)
            for d in docs:
                all_docs.append({
                    "page_content": d.page_content,
                    "metadata": dict(d.metadata),
                })
        except Exception as e:
            logger.warning("load_knowledge_docs(%s) failed: %s", path, e)

    _loaded_docs = all_docs
    logger.info("loaded %d knowledge doc chunks from disk", len(all_docs))
    return all_docs


def _tokenize(text: str) -> list[str]:
    """支持中英文的分词：中文按二元组（bigram）切分，英文按空格切分，数字保留。

    中文使用 bigram 而非单字：单字匹配几乎每个文档都能命中（常见字如"的/是/不"），
    导致 _keyword_match 得分无区分度。bigram 大幅提升匹配精度。
    """
    text = text.strip().lower()
    tokens: list[str] = []
    cjk_buf: list[str] = []  # 连续中文字符缓冲区

    def _flush_cjk() -> None:
        """将缓冲区中的中文字符生成 bigram token。"""
        nonlocal cjk_buf
        if len(cjk_buf) == 1:
            tokens.append(cjk_buf[0])
        else:
            for i in range(len(cjk_buf) - 1):
                tokens.append(cjk_buf[i] + cjk_buf[i + 1])
        cjk_buf = []

    alpha_buf = ""
    for ch in text:
        if "\u4e00" <= ch <= "\u9fff" or "\u3400" <= ch <= "\u4dbf":
            # 中文字符：先提交英文缓冲，再将中文加入 CJK 缓冲区
            if alpha_buf:
                tokens.append(alpha_buf)
                alpha_buf = ""
            cjk_buf.append(ch)
        elif ch.isalnum() or ch in ("-", "_"):
            # 遇到非中文字符，先提交 CJK 缓冲区
            if cjk_buf:
                _flush_cjk()
            alpha_buf += ch
        else:
            if cjk_buf:
                _flush_cjk()
            if alpha_buf:
                tokens.append(alpha_buf)
                alpha_buf = ""
    # 提交残留
    if cjk_buf:
        _flush_cjk()
    if alpha_buf:
        tokens.append(alpha_buf)
    return tokens


def _keyword_match(query: str, docs: list[dict]) -> list[dict]:
    """简单的本地关键词匹配 fallback（Chroma 不可用时）。支持中英文。"""
    keywords = _tokenize(query)
    if not keywords:
        return []
    scored: list[tuple[int, dict]] = []
    for d in docs:
        text = (d.get("page_content") or "").lower()
        score = sum(1 for kw in keywords if kw in text)
        if score > 0:
            scored.append((score, d))
    scored.sort(key=lambda x: -x[0])
    return [d for _, d in scored[:5]]


async def rag_node(state: AgentState) -> dict:
    """从知识库检索相关信息。先尝试 Chroma，失败则直接读文档。"""
    last = state["messages"][-1]
    query = str(last.content if hasattr(last, "content") else last)
    docs: list[dict] = []

    # 1) 尝试 Chroma 向量检索
    try:
        retriever = HybridRetriever()
        results = retriever.retrieve(str(query), top_k=5)
        docs = [
            {"page_content": d.page_content, "metadata": dict(d.metadata)}
            for d in results
        ]
    except Exception as e:
        logger.warning("Chroma retrieve failed: %s", e)

    # 2) Chroma 无结果 → fallback 直接读 markdown
    if not docs:
        logger.info("Chroma returned no results, falling back to direct doc reading")
        try:
            all_docs = _load_knowledge_docs()
            docs = _keyword_match(query, all_docs)
        except Exception as e:
            logger.warning("fallback doc loading also failed: %s", e)

    # 3) 仍无结果 → 确认是否有知识文件存在
    if not docs:
        project_root = _get_project_root()
        knowledge_dir = project_root / "data" / "knowledge"
        count = sum(1 for _ in knowledge_dir.rglob("*") if _.is_file() and _.suffix in (".md", ".txt", ".json"))
        if count > 0:
            logger.info("no match for query but %d knowledge files exist", count)

    return {"retrieved_docs": docs}
