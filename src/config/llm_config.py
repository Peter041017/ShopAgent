"""LLM 提供商与模型相关集中配置（可按环境扩展）。"""

from src.config.settings import settings

LLM_DEFAULT_TEMPERATURE = settings.LLM_MODEL_TEMPERATURE

# 与 LangChain ChatOpenAI 一致：api_key / base_url 取自 settings（默认 DeepSeek 兼容端点）
CHAT_LLM_MODEL = settings.LLM_MODEL
