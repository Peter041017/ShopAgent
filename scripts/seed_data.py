"""本地开发：写入示例会话/占位数据（可按需扩展）"""
import json
from pathlib import Path


def main() -> None:
    root = Path(__file__).resolve().parent.parent / "data" / "knowledge" / "faq"
    root.mkdir(parents=True, exist_ok=True)
    faq = [
        {
            "question": "支持花呗分期吗？",
            "answer": "支持花呗 3/6/12 期分期，具体费率以收银台为准。",
            "tags": ["支付"],
        }
    ]
    (root / "sample_faq.json").write_text(
        json.dumps(faq, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"已写入 {root / 'sample_faq.json'}")


if __name__ == "__main__":
    main()
