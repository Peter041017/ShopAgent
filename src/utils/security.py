"""内容安全审核 — 检测敏感词、注入攻击、垃圾信息。"""

import re

from src.utils.logger import get_logger

logger = get_logger(__name__)

# 敏感内容模式
_BLOCKED_PATTERNS: list[re.Pattern] = [
    re.compile(r"(?i)\b(?:暴力|色情|赌博|毒品|枪支|炸药)\b"),
    re.compile(r"(?i)\b(?:hack|crack|exploit|malware|ransomware)\b"),
    re.compile(r"(?i)(?:system\s*prompt|ignore\s*all|forget\s*previous)"),
    re.compile(r"(?i)(?:重复\s*以上|忽略\s*以上)"),
]

# 疑似注入检测
_INJECTION_PATTERNS: list[re.Pattern] = [
    re.compile(r"(?i)(?:你是一个|你是\w+机器人|扮演|role\s*:|system\s*:)"),
    re.compile(r"(?i)\bselect\b.+\bfrom\b"),
]

# 垃圾信息检测：连续重复字符 / 纯拼音 / 超长无空格
_SPAM_PATTERNS: list[re.Pattern] = [
    re.compile(r"(.)\1{10,}"),  # 同一字符连续 10+ 次
    re.compile(r"[\u4e00-\u9fff]{0,5}[a-z]{20,}"),  # 长段拼音无汉字
    re.compile(r"[\w\s]{200,}"),  # 超长无意义内容
]


def _check_blocked(text: str) -> str | None:
    """返回匹配的第一个违规原因，或 None。"""
    for pat in _BLOCKED_PATTERNS:
        m = pat.search(text)
        if m:
            return f"包含敏感内容: {m.group()}"
    return None


def _check_injection(text: str) -> bool:
    return any(p.search(text) for p in _INJECTION_PATTERNS)


def _check_spam(text: str) -> bool:
    return any(p.search(text) for p in _SPAM_PATTERNS)


def screen_user_text(text: str) -> tuple[bool, str]:
    """
    对用户输入进行安全检查。

    Returns:
        (是否通过, 原因描述)
    """
    if not text or not text.strip():
        return False, "消息为空"

    # 1. 敏感内容拦截
    reason = _check_blocked(text)
    if reason:
        logger.warning("security block: %s", reason)
        return False, reason

    # 2. 提示注入检测
    if _check_injection(text):
        logger.warning("security block: detected prompt injection")
        return False, "检测到疑似提示注入，请求被拦截"

    # 3. 垃圾信息检测
    if _check_spam(text):
        logger.warning("security block: detected spam content")
        return False, "检测到疑似垃圾信息，请正常输入"

    return True, "ok"
