from functools import lru_cache
from pathlib import Path

from pydantic import AliasChoices, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=Path(__file__).resolve().parent.parent.parent / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # 对话 LLM：OpenAI 兼容客户端（DeepSeek / OpenAI 等共用 ChatOpenAI）
    # 环境变量可用 OPENAI_* 或 DEEPSEEK_*（后者便于区分「只配了 DeepSeek」）
    OPENAI_API_KEY: str = Field(
        default="",
        validation_alias=AliasChoices("OPENAI_API_KEY", "DEEPSEEK_API_KEY"),
    )
    OPENAI_BASE_URL: str = Field(
        default="https://api.deepseek.com/v1",
        validation_alias=AliasChoices("OPENAI_BASE_URL", "DEEPSEEK_BASE_URL"),
    )
    LLM_MODEL: str = Field(
        default="deepseek-v4-pro",
        validation_alias=AliasChoices("LLM_MODEL", "DEEPSEEK_MODEL"),
    )
    LLM_MODEL_TEMPERATURE: float = 0.3

    # 向量嵌入：若对话走 DeepSeek，嵌入常需单独 OpenAI 兼容服务（留空则回退到上面的 Key/Base）
    EMBEDDING_OPENAI_API_KEY: str = Field(
        default="",
        validation_alias=AliasChoices(
            "EMBEDDING_OPENAI_API_KEY",
            "EMBEDDING_API_KEY",
        ),
    )
    EMBEDDING_OPENAI_BASE_URL: str = Field(
        default="",
        validation_alias=AliasChoices(
            "EMBEDDING_OPENAI_BASE_URL",
            "EMBEDDING_BASE_URL",
        ),
    )
    EMBEDDING_MODEL: str = "text-embedding-3-small"

    VECTOR_STORE_TYPE: str = "chroma"
    CHROMA_PERSIST_DIR: str = "./data/chroma"
    CHROMA_COLLECTION_NAME: str = "shop_knowledge"

    # 数据库：留空自动回退到 SQLite (data/shopagent.db)；生产环境设为 postgresql+asyncpg://...
    DATABASE_URL: str = ""
    REDIS_URL: str = "redis://localhost:6379/0"

    LANGSMITH_API_KEY: str = ""
    LANGSMITH_PROJECT: str = "shopagent"

    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = True
    MAX_CONCURRENT_SESSIONS: int = 100


@lru_cache
def get_settings() -> Settings:
    return Settings()


class _SettingsProxy:
    __slots__ = ()

    def __getattr__(self, name: str):
        return getattr(get_settings(), name)


settings = _SettingsProxy()
