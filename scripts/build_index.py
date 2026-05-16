"""构建向量索引：加载知识文档并写入 Chroma。"""
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.rag.indexer import build_default_index


def count_files(category: str) -> int:
    base = Path("data/knowledge") / category
    if not base.exists():
        return 0
    return sum(1 for f in base.rglob("*") if f.is_file() and f.suffix.lower() in (".md", ".txt", ".csv", ".json"))


def main() -> None:
    start = time.perf_counter()
    print("=" * 50)
    print("ShopAgent 知识库索引构建")
    print("=" * 50)

    for cat in ("products", "policies", "faq"):
        n = count_files(cat)
        print(f"  {cat}: {n} 个文件")

    print()

    n = build_default_index()
    elapsed = time.perf_counter() - start
    print(f"\n[ok] 索引构建完成，共 {n} 个文档块，耗时 {elapsed:.2f}s")
    print(f"  Chroma 持久目录: data/chroma")


if __name__ == "__main__":
    main()
