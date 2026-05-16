from langchain_openai import OpenAIEmbeddings

from src.config.settings import settings


def get_embeddings() -> OpenAIEmbeddings:
    # 无 Key 时仍构造客户端，便于仅跑图/单测；真正调用嵌入接口会失败直至配置 .env
    api_key = (
        settings.EMBEDDING_OPENAI_API_KEY or settings.OPENAI_API_KEY
    ) or "sk-placeholder-not-for-production"
    base_url = settings.EMBEDDING_OPENAI_BASE_URL or settings.OPENAI_BASE_URL or None
    return OpenAIEmbeddings(
        model=settings.EMBEDDING_MODEL,
        api_key=api_key,
        base_url=base_url,
    )
