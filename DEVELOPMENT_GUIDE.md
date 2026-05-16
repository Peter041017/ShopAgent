# 智能电商客服 Agent 开发文档

> 基于 Python + LangChain + LangGraph + RAG 的智能客服系统

---

## 目录

1. [项目概述](#1-项目概述)
2. [技术选型](#2-技术选型)
3. [系统架构](#3-系统架构)
4. [项目结构](#4-项目结构)
5. [环境搭建](#5-环境搭建)
6. [核心模块实现](#6-核心模块实现)
   - [6.1 知识库构建 (RAG)](#61-知识库构建-rag)
   - [6.2 检索器](#62-检索器)
   - [6.3 工具定义](#63-工具定义)
   - [6.4 LangGraph 状态图](#64-langgraph-状态图)
   - [6.5 对话管理](#65-对话管理)
   - [6.6 意图识别与路由](#66-意图识别与路由)
   - [6.7 API 服务层](#67-api-服务层)
7. [运行与测试](#7-运行与测试)
8. [部署方案](#8-部署方案)
9. [扩展方向](#9-扩展方向)

---

## 1. 项目概述

### 1.1 目标

构建一个智能电商客服 Agent，具备以下能力：

- **商品咨询**：解答商品规格、价格、库存等问题
- **订单处理**：查询订单状态、物流跟踪、退换货流程
- **售后支持**：处理退款、投诉、发票等售后问题
- **个性化推荐**：基于用户画像和对话上下文推荐商品
- **多轮对话**：维护上下文，支持追问和澄清
- **人工转接**：复杂问题无缝转接人工客服

### 1.2 核心设计原则

| 原则 | 说明 |
|------|------|
| RAG 优先 | 知识库问答优先于模型生成，减少幻觉 |
| 工具增强 | 通过 Function Calling 对接真实业务接口 |
| 状态驱动 | LangGraph 管理多轮对话状态与流程控制 |
| 可观测 | 全链路日志与追踪，便于调试和优化 |

---

## 2. 技术选型

| 层面 | 技术 | 说明 |
|------|------|------|
| 语言 | Python 3.11+ | 生态成熟，AI/ML 库丰富 |
| LLM 框架 | LangChain 0.3+ | 统一 LLM 调用抽象 |
| 流程编排 | LangGraph 0.2+ | 有状态多步 Agent 工作流 |
| 向量数据库 | ChromaDB / Milvus | 轻量级嵌入式向量存储，生产可用 Milvus |
| Embedding | text-embedding-3-small / BGE-M3 | 文本向量化，BGE-M3 支持中英双语 |
| LLM | GPT-4o / Claude Sonnet 4 / DeepSeek-V3 | 按成本与效果灵活切换 |
| API 框架 | FastAPI | 高性能异步 Web 框架 |
| 缓存 | Redis | 会话缓存与热点知识缓存 |
| 消息队列 | Redis Streams / RabbitMQ | 异步任务如邮件发送、物流查询 |
| 存储 | PostgreSQL + MinIO | 结构化数据 + 文件/图片存储 |
| 监控 | LangSmith / LangFuse | LLM 调用链追踪与评估 |

---

## 3. 系统架构

### 3.1 整体架构图

```
┌─────────────────────────────────────────────────────────────┐
│                        前端层                                │
│   Web Chat Widget  │   Mobile App  │   WeChat Mini Program   │
└────────────────────────┬────────────────────────────────────┘
                         │  WebSocket / HTTP
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                      API 网关层                              │
│              FastAPI + WebSocket + Rate Limiter             │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                     Agent 编排层                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │                   LangGraph                          │   │
│  │  ┌─────────┐  ┌──────────┐  ┌──────────────────┐   │   │
│  │  │ 意图路由 │→│ 子 Agent  │→│ 工具调用 / 知识检索 │   │   │
│  │  └─────────┘  └──────────┘  └──────────────────┘   │   │
│  └─────────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              对话管理 & 记忆系统                      │   │
│  │  短期记忆 (Buffer)  │  长期记忆 (Summary)  │  用户画像 │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                         │
          ┌──────────────┼──────────────┐
          ▼              ▼              ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│   RAG 引擎    │ │   工具层      │ │   知识库      │
│  Embedding   │ │  订单查询     │ │  商品文档     │
│  检索+重排序  │ │  物流追踪     │ │  政策规则     │
│  混合检索     │ │  退款处理     │ │  FAQ 库      │
└──────────────┘ └──────────────┘ └──────────────┘
          │              │              │
          └──────────────┼──────────────┘
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                      数据 & 基础设施层                        │
│  PostgreSQL  │  Redis  │  ChromaDB/Milvus  │  MinIO/OSS    │
└─────────────────────────────────────────────────────────────┘
```

### 3.2 Agent 决策流程

```
用户消息
    │
    ▼
┌──────────┐    是     ┌──────────────┐
│ 安全审核  │─────────▶│ 拒绝 + 提示   │
└────┬─────┘          └──────────────┘
     │ 通过
     ▼
┌──────────┐  知识类   ┌──────────────┐
│ 意图识别  │─────────▶│ RAG 检索回答  │
└────┬─────┘          └──────────────┘
     │ 操作类
     ▼
┌──────────┐  需澄清   ┌──────────────┐
│ 槽位填充  │─────────▶│ 追问用户      │
└────┬─────┘          └──────────────┘
     │ 槽位齐全
     ▼
┌──────────┐           ┌──────────────┐
│ 工具调用  │──────────▶│ 生成最终回复   │
└──────────┘           └──────────────┘
```

---

## 4. 项目结构

```
ShopAgent/
├── pyproject.toml                 # 项目配置与依赖管理
├── .env.example                   # 环境变量模板
├── docker-compose.yml             # 本地开发基础设施
├── Makefile                       # 常用命令快捷方式
│
├── src/
│   ├── __init__.py
│   ├── main.py                    # FastAPI 入口
│   │
│   ├── config/
│   │   ├── __init__.py
│   │   ├── settings.py            # 配置管理 (pydantic-settings)
│   │   └── llm_config.py          # LLM 提供商配置
│   │
│   ├── agent/
│   │   ├── __init__.py
│   │   ├── graph.py               # LangGraph 状态图定义
│   │   ├── state.py               # Agent 状态 Schema
│   │   ├── nodes/                 # 图节点
│   │   │   ├── __init__.py
│   │   │   ├── intent_router.py   # 意图识别节点
│   │   │   ├── rag_node.py        # RAG 检索节点
│   │   │   ├── tool_node.py       # 工具调用节点
│   │   │   ├── clarification.py   # 澄清追问节点
│   │   │   └── response_gen.py    # 回复生成节点
│   │   └── edges/                 # 条件边逻辑
│   │       ├── __init__.py
│   │       └── routers.py         # 路由判断函数
│   │
│   ├── rag/
│   │   ├── __init__.py
│   │   ├── embeddings.py          # Embedding 模型封装
│   │   ├── vector_store.py        # 向量数据库操作
│   │   ├── retriever.py           # 检索器（混合检索+重排序）
│   │   ├── loader.py              # 文档加载与分块
│   │   └── indexer.py             # 索引构建脚本
│   │
│   ├── tools/
│   │   ├── __init__.py
│   │   ├── order_tools.py         # 订单相关工具
│   │   ├── product_tools.py       # 商品相关工具
│   │   ├── logistics_tools.py     # 物流相关工具
│   │   └── refund_tools.py        # 退款相关工具
│   │
│   ├── memory/
│   │   ├── __init__.py
│   │   ├── buffer.py              # 短期对话缓冲
│   │   └── summary.py             # 长期摘要记忆
│   │
│   ├── api/
│   │   ├── __init__.py
│   │   ├── routes/
│   │   │   ├── __init__.py
│   │   │   ├── chat.py            # 聊天接口
│   │   │   ├── admin.py           # 管理后台接口
│   │   │   └── knowledge.py       # 知识库管理接口
│   │   ├── middleware.py           # 中间件（限流、日志、认证）
│   │   └── schemas.py             # 请求/响应 Pydantic 模型
│   │
│   └── utils/
│       ├── __init__.py
│       ├── logger.py              # 日志配置
│       ├── prompts.py             # Prompt 模板管理
│       └── security.py            # 内容安全审核
│
├── data/
│   ├── knowledge/                 # 原始知识文档
│   │   ├── products/              # 商品说明文档
│   │   ├── policies/              # 售后政策文档
│   │   └── faq/                   # 常见问题
│   └── chroma/                    # ChromaDB 持久化目录
│
├── scripts/
│   ├── build_index.py             # 构建知识库索引
│   ├── eval_rag.py                # RAG 效果评估
│   └── seed_data.py               # 测试数据填充
│
├── tests/
│   ├── conftest.py
│   ├── test_agent.py
│   ├── test_rag.py
│   └── test_tools.py
│
└── docs/
    └── api.md                     # API 文档
```

---

## 5. 环境搭建

### 5.1 pyproject.toml

```toml
[project]
name = "shopagent"
version = "0.1.0"
description = "智能电商客服Agent"
requires-python = ">=3.11"
dependencies = [
    "langchain>=0.3.0",
    "langgraph>=0.2.0",
    "langchain-openai>=0.2.0",
    "langchain-community>=0.3.0",
    "chromadb>=0.5.0",
    "fastapi>=0.115.0",
    "uvicorn[standard]>=0.30.0",
    "websockets>=13.0",
    "redis>=5.0.0",
    "pydantic>=2.0.0",
    "pydantic-settings>=2.0.0",
    "python-dotenv>=1.0.0",
    "tiktoken>=0.7.0",
    "httpx>=0.27.0",
    "sqlalchemy>=2.0.0",
    "asyncpg>=0.29.0",
    "alembic>=1.13.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0",
    "pytest-asyncio>=0.24.0",
    "langsmith>=0.1.0",
    "langfuse>=2.0.0",
]
milvus = ["pymilvus>=2.4.0"]

[tool.ruff]
line-length = 100
target-version = "py311"

[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["tests"]
```

### 5.2 docker-compose.yml （本地开发基础设施）

```yaml
version: "3.9"
services:
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

  postgres:
    image: pgvector/pgvector:pg16
    ports:
      - "5432:5432"
    environment:
      POSTGRES_USER: shopagent
      POSTGRES_PASSWORD: shopagent
      POSTGRES_DB: shopagent
    volumes:
      - pg_data:/var/lib/postgresql/data

  chroma:
    image: chromadb/chroma:latest
    ports:
      - "8001:8000"
    volumes:
      - chroma_data:/chroma/chroma

volumes:
  redis_data:
  pg_data:
  chroma_data:
```

### 5.3 环境变量 (.env.example)

```bash
# LLM 配置
OPENAI_API_KEY=sk-xxx
OPENAI_BASE_URL=https://api.openai.com/v1
LLM_MODEL=gpt-4o
LLM_MODEL_TEMPERATURE=0.3

# Embedding 配置
EMBEDDING_MODEL=text-embedding-3-small

# 向量库
VECTOR_STORE_TYPE=chroma
CHROMA_PERSIST_DIR=./data/chroma
CHROMA_COLLECTION_NAME=shop_knowledge

# 数据库
DATABASE_URL=postgresql+asyncpg://shopagent:shopagent@localhost:5432/shopagent

# Redis
REDIS_URL=redis://localhost:6379/0

# LangSmith 追踪
LANGSMITH_API_KEY=ls-xxx
LANGSMITH_PROJECT=shopagent

# 服务配置
HOST=0.0.0.0
PORT=8000
DEBUG=true
MAX_CONCURRENT_SESSIONS=100
```

### 5.4 启动步骤

```bash
# 1. 创建虚拟环境
python -m venv .venv && source .venv/bin/activate   # Linux/Mac
# python -m venv .venv && .venv\Scripts\activate     # Windows

# 2. 安装依赖
pip install -e ".[dev]"

# 3. 启动基础设施
docker compose up -d

# 4. 配置环境变量
cp .env .env   # 编辑填入真实 API Key

# 5. 构建知识库索引
python scripts/build_index.py

# 6. 启动服务
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

---

## 6. 核心模块实现

> **实现注意事项 (v0.1.1 更新)**：
> 1. **RAG 中文分词**：Chroma 不可用时的回退关键词匹配已从单字切分升级为 bigram 二元组切分（`rag_node._tokenize()`），中文查询匹配精度大幅提升。
> 2. **JSON 泄漏防护**：WebSocket 流式过滤、HTTP 响应、response_gen 节点均已加入意图 JSON 正则清洗 + 状态重置，防止 `intent_router` 的 JSON 输出泄漏到用户回复中。
> 3. **状态防泄漏**：每次 `agent.ainvoke()` 前显式重置 `final_response` 和 `_security_blocked`，避免 `MemorySaver` 缓存的旧值残留。

### 6.1 知识库构建 (RAG)

#### 6.1.1 文档加载与分块 (`src/rag/loader.py`)

```python
from langchain_community.document_loaders import (
    TextLoader,
    CSVLoader,
    UnstructuredMarkdownLoader,
    JSONLoader,
)
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
from pathlib import Path


class DocumentLoader:
    """加载各种格式的电商知识文档"""

    LOADER_MAP = {
        ".txt": TextLoader,
        ".csv": CSVLoader,
        ".md": UnstructuredMarkdownLoader,
        ".json": JSONLoader,
    }

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

    def load_directory(self, path: str) -> list[Document]:
        docs = []
        for file_path in Path(path).rglob("*"):
            if file_path.suffix in self.LOADER_MAP:
                loader_cls = self.LOADER_MAP[file_path.suffix]
                loader = loader_cls(str(file_path), encoding="utf-8")
                loaded = loader.load()
                # 添加来源元数据
                for doc in loaded:
                    doc.metadata["source"] = str(file_path)
                    doc.metadata["category"] = file_path.parent.name
                docs.extend(loaded)
        return self.text_splitter.split_documents(docs)

    def load_faq(self, faq_data: list[dict]) -> list[Document]:
        """加载 FAQ 数据，以 Q 为检索单元"""
        docs = []
        for item in faq_data:
            docs.append(Document(
                page_content=f"Q: {item['question']}\nA: {item['answer']}",
                metadata={"type": "faq", "tags": item.get("tags", [])},
            ))
        return docs
```

#### 6.1.2 Embedding 封装 (`src/rag/embeddings.py`)

```python
from langchain_openai import OpenAIEmbeddings
from src.config.settings import settings


def get_embeddings() -> OpenAIEmbeddings:
    return OpenAIEmbeddings(
        model=settings.EMBEDDING_MODEL,
        openai_api_key=settings.OPENAI_API_KEY,
        openai_api_base=settings.OPENAI_BASE_URL,
    )
```

#### 6.1.3 向量存储 (`src/rag/vector_store.py`)

```python
from langchain_chroma import Chroma
from src.rag.embeddings import get_embeddings
from src.config.settings import settings


class VectorStoreManager:
    def __init__(self):
        self.embeddings = get_embeddings()
        self._store = None

    @property
    def store(self) -> Chroma:
        if self._store is None:
            self._store = Chroma(
                collection_name=settings.CHROMA_COLLECTION_NAME,
                embedding_function=self.embeddings,
                persist_directory=settings.CHROMA_PERSIST_DIR,
            )
        return self._store

    def add_documents(self, docs: list, batch_size: int = 100):
        for i in range(0, len(docs), batch_size):
            batch = docs[i:i + batch_size]
            self.store.add_documents(batch)

    def search(
        self, query: str, k: int = 5, filter: dict | None = None
    ) -> list:
        return self.store.similarity_search_with_score(
            query, k=k, filter=filter
        )


vector_store_manager = VectorStoreManager()
```

#### 6.1.4 索引构建脚本 (`scripts/build_index.py`)

```python
"""首次运行或知识更新时执行，构建向量索引"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.rag.loader import DocumentLoader
from src.rag.vector_store import vector_store_manager


def main():
    loader = DocumentLoader(chunk_size=800, chunk_overlap=120)

    print("[1/3] 加载商品文档...")
    product_docs = loader.load_directory("data/knowledge/products")

    print("[2/3] 加载政策文档...")
    policy_docs = loader.load_directory("data/knowledge/policies")

    print("[3/3] 构建向量索引...")
    all_docs = product_docs + policy_docs
    vector_store_manager.add_documents(all_docs)

    print(f"索引构建完成，共 {len(all_docs)} 个文档块")


if __name__ == "__main__":
    main()
```

---

### 6.2 检索器

#### 混合检索与重排序 (`src/rag/retriever.py`)

```python
from langchain.retrievers import ContextualCompressionRetriever
from langchain.retrievers.document_compressors import CrossEncoderReranker
from langchain_community.cross_encoders import HuggingFaceCrossEncoder
from langchain.schema import Document
from langchain_core.runnables import RunnableConfig

from src.rag.vector_store import vector_store_manager


class HybridRetriever:
    """混合检索器：向量检索 + 关键词检索 + 重排序"""

    def __init__(self, rerank_model: str = "BAAI/bge-reranker-v2-m3"):
        self.vector_store = vector_store_manager.store

        # 重排序模型（首次加载较慢，可考虑服务化）
        self.reranker = CrossEncoderReranker(
            model=HuggingFaceCrossEncoder(model_name=rerank_model),
            top_n=5,
        )

    def retrieve(
        self,
        query: str,
        top_k: int = 10,
        filter: dict | None = None,
    ) -> list[Document]:
        # 1. 向量相似度检索（多召回一些候选）
        retriever = self.vector_store.as_retriever(
            search_type="similarity",
            search_kwargs={"k": top_k * 2, "filter": filter},
        )

        # 2. 关键词检索（BM25 增强召回）
        bm25_retriever = self.vector_store.as_retriever(
            search_type="mmr",
            search_kwargs={"k": top_k, "fetch_k": top_k * 3, "filter": filter},
        )

        # 3. 合并去重
        vector_docs = retriever.invoke(query)
        bm25_docs = bm25_retriever.invoke(query)
        all_docs = self._deduplicate(vector_docs + bm25_docs)

        # 4. 重排序
        compression_retriever = ContextualCompressionRetriever(
            base_compressor=self.reranker,
            base_retriever=retriever,
        )
        reranked = compression_retriever.compress_documents(
            documents=all_docs[: top_k * 2],
            query=query,
        )
        return reranked[:top_k]

    def _deduplicate(self, docs: list[Document]) -> list[Document]:
        seen = set()
        unique = []
        for doc in docs:
            key = doc.page_content
            if key not in seen:
                seen.add(key)
                unique.append(doc)
        return unique
```

---

### 6.3 工具定义

#### 6.3.1 订单工具 (`src/tools/order_tools.py`)

```python
from langchain_core.tools import tool
from pydantic import BaseModel, Field


class OrderQueryInput(BaseModel):
    order_id: str = Field(description="订单号")
    user_id: str = Field(description="用户ID")


class OrderStatusInput(BaseModel):
    user_id: str = Field(description="用户ID")
    status_filter: str = Field(
        default="all",
        description="订单状态筛选：pending/paid/shipped/delivered/cancelled",
    )


@tool(args_schema=OrderQueryInput)
async def query_order(order_id: str, user_id: str) -> str:
    """查询指定订单的详细信息，包括商品、金额、状态、物流等"""
    # 实际对接订单数据库或微服务
    # 示例返回
    return f"""
订单号: {order_id}
状态: 已发货
商品: iPhone 16 Pro 256GB 沙漠金 x1
金额: ¥8,999.00
下单时间: 2026-05-14 10:30:00
物流: 顺丰速运 SF1234567890
预计送达: 2026-05-16
    """.strip()


@tool(args_schema=OrderStatusInput)
async def list_user_orders(user_id: str, status_filter: str = "all") -> str:
    """查询用户订单列表，可按状态筛选"""
    return f"用户 {user_id} 的订单列表：共 3 笔订单..."
```

#### 6.3.2 商品工具 (`src/tools/product_tools.py`)

```python
from langchain_core.tools import tool
from pydantic import BaseModel, Field


class ProductSearchInput(BaseModel):
    keyword: str = Field(description="搜索关键词")
    category: str = Field(default="", description="商品分类")
    price_min: float = Field(default=0, description="最低价格")
    price_max: float = Field(default=999999, description="最高价格")


@tool(args_schema=ProductSearchInput)
async def search_products(
    keyword: str,
    category: str = "",
    price_min: float = 0,
    price_max: float = 999999,
) -> str:
    """搜索商品，支持关键词、分类、价格区间筛选"""
    # 实际对接商品搜索服务（Elasticsearch / Meilisearch）
    return f"搜索 '{keyword}' 的结果：找到 15 件商品..."
```

#### 6.3.3 工具注册中心

```python
# src/tools/__init__.py
from src.tools.order_tools import query_order, list_user_orders
from src.tools.product_tools import search_products
from src.tools.logistics_tools import track_logistics
from src.tools.refund_tools import query_refund_policy, submit_refund

ALL_TOOLS = [
    query_order,
    list_user_orders,
    search_products,
    track_logistics,
    query_refund_policy,
    submit_refund,
]

# 危险操作需人工确认
DANGEROUS_TOOLS = {submit_refund.name}
```

---

### 6.4 LangGraph 状态图

#### 6.4.1 状态定义 (`src/agent/state.py`)

```python
from __future__ import annotations
from typing import TypedDict, Annotated, Literal
from langchain.schema import BaseMessage
from langgraph.graph.message import add_messages


class AgentState(TypedDict):
    # 对话消息（自动合并新消息）
    messages: Annotated[list[BaseMessage], add_messages]

    # 用户信息
    user_id: str
    session_id: str

    # 意图识别结果
    intent: Literal["product_inquiry", "order_query", "after_sales", "chitchat", "unknown"]

    # RAG 检索到的知识文档
    retrieved_docs: list

    # 工具调用结果
    tool_results: list[dict]

    # 是否需要人工转接
    needs_human: bool

    # 是否需要澄清追问
    needs_clarification: bool
    clarification_question: str

    # 槽位填充（追踪用户已提供的信息）
    slots: dict

    # 最终回复
    final_response: str
```

#### 6.4.2 图定义 (`src/agent/graph.py`)

```python
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver

from src.agent.state import AgentState
from src.agent.nodes.intent_router import intent_router_node
from src.agent.nodes.rag_node import rag_node
from src.agent.nodes.tool_node import tool_executor_node
from src.agent.nodes.clarification import clarification_node
from src.agent.nodes.response_gen import response_generation_node
from src.agent.edges.routers import route_after_intent, route_after_tool


def build_agent_graph() -> StateGraph:
    workflow = StateGraph(AgentState)

    # 添加节点
    workflow.add_node("intent_router", intent_router_node)
    workflow.add_node("rag_retrieval", rag_node)
    workflow.add_node("tool_executor", tool_executor_node)
    workflow.add_node("clarification", clarification_node)
    workflow.add_node("response_gen", response_generation_node)

    # 入口
    workflow.add_edge(START, "intent_router")

    # 意图路由 → 分流
    workflow.add_conditional_edges(
        "intent_router",
        route_after_intent,
        {
            "rag": "rag_retrieval",
            "tool": "tool_executor",
            "clarify": "clarification",
            "respond": "response_gen",
        },
    )

    # RAG → 回复
    workflow.add_edge("rag_retrieval", "response_gen")

    # 工具执行 → 判断是否继续
    workflow.add_conditional_edges(
        "tool_executor",
        route_after_tool,
        {
            "respond": "response_gen",
            "clarify": "clarification",
            "retry": "tool_executor",
        },
    )

    # 澄清 → 等待用户回复（结束本轮）
    workflow.add_edge("clarification", END)

    # 回复 → 结束
    workflow.add_edge("response_gen", END)

    return workflow


def create_agent():
    """创建可编译执行的 Agent"""
    workflow = build_agent_graph()
    memory = MemorySaver()  # 生产环境替换为 PostgresSaver / RedisSaver
    return workflow.compile(checkpointer=memory)
```

#### 6.4.3 条件路由 (`src/agent/edges/routers.py`)

```python
from src.agent.state import AgentState


def route_after_intent(state: AgentState) -> str:
    """根据意图决定下一个节点"""
    intent = state.get("intent", "unknown")

    if intent in ("product_inquiry",):
        return "rag"  # 商品咨询走知识检索
    elif intent in ("order_query", "after_sales"):
        return "tool"  # 订单售后走工具调用
    elif state.get("needs_clarification"):
        return "clarify"
    else:
        return "respond"


def route_after_tool(state: AgentState) -> str:
    """工具执行后的路由"""
    if state.get("needs_clarification"):
        return "clarify"
    elif state.get("needs_human"):
        return "respond"  # 人工转接提示在 response 中处理
    return "respond"
```

---

### 6.5 对话管理

#### 6.5.1 短期记忆 (`src/memory/buffer.py`)

```python
from langchain.memory import ConversationBufferWindowMemory
from langchain.schema import BaseMessage


class ConversationMemory:
    """封装对话缓冲，只保留最近 N 轮"""

    def __init__(self, max_turns: int = 10):
        self.max_turns = max_turns

    def get_messages(self, session_id: str) -> list[BaseMessage]:
        """从 Redis 读取会话历史"""
        # 生产实现：Redis List + 序列化
        pass

    def add_message(self, session_id: str, message: BaseMessage):
        """追加消息到 Redis"""
        pass

    def get_context_window(self, session_id: str, max_tokens: int = 4000) -> str:
        """获取格式化上下文，控制在 token 预算内"""
        messages = self.get_messages(session_id)
        # 从最新往前取，用 tiktoken 计数控制总 token
        pass
```

#### 6.5.2 长期摘要记忆 (`src/memory/summary.py`)

```python
from langchain.memory import ConversationSummaryMemory
from langchain_openai import ChatOpenAI
from src.config.settings import settings


class SummaryMemory:
    """对超过窗口的消息做摘要压缩，保留关键信息"""

    def __init__(self):
        self.llm = ChatOpenAI(
            model=settings.LLM_MODEL,
            temperature=0.2,
            api_key=settings.OPENAI_API_KEY,
        )

    def summarize(self, messages: list) -> str:
        """对历史对话生成摘要"""
        prompt = "请用 2-3 句话总结以下对话，保留用户需求和关键信息:\n\n"
        history = "\n".join(
            f"{'用户' if m.type == 'human' else '客服'}: {m.content}"
            for m in messages
        )
        response = self.llm.invoke(prompt + history)
        return response.content
```

---

### 6.6 意图识别与路由

#### 意图识别节点 (`src/agent/nodes/intent_router.py`)

```python
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from src.agent.state import AgentState
from src.config.settings import settings
from src.utils.prompts import INTENT_SYSTEM_PROMPT


async def intent_router_node(state: AgentState) -> dict:
    """识别用户意图并提取槽位信息"""

    llm = ChatOpenAI(
        model=settings.LLM_MODEL,
        temperature=0.1,
        api_key=settings.OPENAI_API_KEY,
    )

    user_message = state["messages"][-1].content

    response = await llm.ainvoke([
        SystemMessage(content=INTENT_SYSTEM_PROMPT),
        HumanMessage(content=user_message),
    ])

    # 解析 LLM 返回的 JSON
    import json
    try:
        result = json.loads(response.content)
    except json.JSONDecodeError:
        result = {"intent": "unknown", "slots": {}, "needs_clarification": False}

    return {
        "intent": result.get("intent", "unknown"),
        "slots": result.get("slots", {}),
        "needs_clarification": result.get("needs_clarification", False),
        "clarification_question": result.get("clarification_question", ""),
    }
```

#### Intent Prompt (`src/utils/prompts.py`)

```python
INTENT_SYSTEM_PROMPT = """你是一个电商客服意图识别器。分析用户消息，输出 JSON：

{
  "intent": "product_inquiry|order_query|after_sales|chitchat",
  "slots": {
    "order_id": "提取的订单号或null",
    "product_name": "提取的商品名或null",
    "issue_type": "退货|换货|退款|投诉|null"
  },
  "needs_clarification": true/false,
  "clarification_question": "如需澄清，追问什么"
}

规则：
- product_inquiry: 商品咨询、规格、价格、推荐
- order_query: 订单状态、物流查询
- after_sales: 退货、换货、退款、投诉
- chitchat: 问候、闲聊
- 如果用户信息不足以确定操作对象（如说"我的订单"但没给订单号），设置 needs_clarification=true
"""
```

---

### 6.7 API 服务层

#### FastAPI 入口 (`src/main.py`)

```python
import uuid
from contextlib import asynccontextmanager

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from src.api.routes import chat, admin, knowledge
from src.config.settings import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动时初始化
    from src.agent.graph import create_agent
    app.state.agent = create_agent()
    yield
    # 关闭时清理
    pass


app = FastAPI(
    title="ShopAgent - 智能电商客服",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat.router, prefix="/api/v1", tags=["聊天"])
app.include_router(admin.router, prefix="/api/v1/admin", tags=["管理"])
app.include_router(knowledge.router, prefix="/api/v1/knowledge", tags=["知识库"])
```

#### 聊天接口 (`src/api/routes/chat.py`)

```python
import uuid
from fastapi import APIRouter, Request
from pydantic import BaseModel
from langchain_core.messages import HumanMessage

router = APIRouter()


class ChatRequest(BaseModel):
    user_id: str
    session_id: str | None = None
    message: str


class ChatResponse(BaseModel):
    session_id: str
    reply: str
    intent: str | None = None
    needs_human: bool = False


@router.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest, request: Request):
    agent = request.app.state.agent
    session_id = req.session_id or str(uuid.uuid4())

    config = {
        "configurable": {
            "thread_id": session_id,
            "user_id": req.user_id,
        }
    }

    result = await agent.ainvoke(
        {"messages": [HumanMessage(content=req.message)]},
        config=config,
    )

    state = result
    return ChatResponse(
        session_id=session_id,
        reply=state.get("final_response", "抱歉，我暂时无法处理您的问题"),
        intent=state.get("intent"),
        needs_human=state.get("needs_human", False),
    )


@router.websocket("/ws/chat")
async def websocket_chat(websocket: WebSocket):
    """WebSocket 端点，支持流式输出"""
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_json()
            # 流式调用 Agent
            agent = websocket.app.state.agent
            config = {"configurable": {"thread_id": data.get("session_id", str(uuid.uuid4()))}}

            async for event in agent.astream_events(
                {"messages": [HumanMessage(content=data["message"])]},
                config=config,
                version="v2",
            ):
                if event["event"] == "on_chat_model_stream":
                    content = event["data"]["chunk"].content
                    if content:
                        await websocket.send_json({"type": "token", "content": content})

            await websocket.send_json({"type": "done"})
    except WebSocketDisconnect:
        pass
```

---

## 7. 运行与测试

### 7.1 单元测试示例 (`tests/test_agent.py`)

```python
import pytest
from langchain_core.messages import HumanMessage
from src.agent.graph import create_agent


@pytest.mark.asyncio
async def test_product_inquiry_flow():
    """测试商品咨询流程"""
    agent = create_agent()
    config = {"configurable": {"thread_id": "test-001", "user_id": "u1"}}

    result = await agent.ainvoke(
        {"messages": [HumanMessage(content="iPhone 16 Pro 有什么颜色")]},
        config=config,
    )

    assert result["intent"] == "product_inquiry"
    assert len(result["final_response"]) > 0


@pytest.mark.asyncio
async def test_multi_turn_conversation():
    """测试多轮对话上下文保持"""
    agent = create_agent()
    config = {"configurable": {"thread_id": "test-002", "user_id": "u1"}}

    # 第一轮
    await agent.ainvoke(
        {"messages": [HumanMessage(content="帮我查订单 ORD-20260514-001")]},
        config=config,
    )

    # 第二轮：省略订单号，依赖上下文
    result = await agent.ainvoke(
        {"messages": [HumanMessage(content="那物流到哪里了")]},
        config=config,
    )

    assert "物流" in result["final_response"] or "SF" in result["final_response"]
```

### 7.2 RAG 评估 (`scripts/eval_rag.py`)

```python
"""RAG 检索效果评估脚本"""
from src.rag.retriever import HybridRetriever


def evaluate():
    retriever = HybridRetriever()
    test_queries = [
        ("iPhone 16 Pro 电池容量是多少", "product"),
        ("退货需要什么条件", "policy"),
        ("你们支持花呗分期吗", "faq"),
    ]

    for query, expected_category in test_queries:
        docs = retriever.retrieve(query, top_k=3)
        print(f"\n查询: {query}")
        for i, doc in enumerate(docs):
            print(f"  #{i+1} [{doc.metadata.get('category')}] {doc.page_content[:80]}...")
```

---

## 8. 部署方案

### 8.1 生产部署架构

```
                    ┌──────────────┐
                    │   Nginx LB   │
                    └──────┬───────┘
                           │
              ┌────────────┼────────────┐
              ▼            ▼            ▼
        ┌──────────┐ ┌──────────┐ ┌──────────┐
        │ FastAPI  │ │ FastAPI  │ │ FastAPI  │
        │ Pod-1    │ │ Pod-2    │ │ Pod-3    │
        └────┬─────┘ └────┬─────┘ └────┬─────┘
             │            │            │
             └────────────┼────────────┘
                          │
        ┌─────────────────┼─────────────────┐
        ▼                 ▼                 ▼
   ┌─────────┐     ┌──────────┐      ┌──────────┐
   │ Redis   │     │ PostgreSQL│      │ Milvus   │
   │ Cluster │     │ Primary+  │      │ Cluster  │
   │         │     │ Read Rep. │      │          │
   └─────────┘     └──────────┘      └──────────┘
```

### 8.2 Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential curl \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml .
RUN pip install --no-cache-dir -e ".[milvus]"

COPY . .

EXPOSE 8000

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

### 8.3 关键配置 Checklist

| 项目 | 说明 |
|------|------|
| `MAX_CONCURRENT_SESSIONS` | 并发会话上限，防止 OOM |
| `LLM_MODEL_TEMPERATURE` | 客服场景建议 0.1-0.3 |
| Embedding 模型维度 | text-embedding-3-small=1536, BGE-M3=1024 |
| ChromaDB → Milvus | 当文档量 > 100 万条时迁移 |
| Redis 内存策略 | allkeys-lru，设置 maxmemory |
| 日志级别 | 生产环境用 INFO，调试时临时开 DEBUG |

---

## 9. 扩展方向

### 9.1 短期（v0.1 → v0.5）

- [ ] 多语言支持（中/英/日/韩）
- [ ] 图文混排回复（商品图片 + 卡片）
- [ ] 情感识别与安抚话术
- [ ] A/B 测试框架（对比不同 Prompt 效果）
- [ ] 知识库自动更新（监听文档变更自动重建索引）

### 9.2 中期（v0.5 → v1.0）

- [ ] 多模态 RAG（支持商品图片以图搜图）
- [ ] 个性化推荐引擎（协同过滤 + LLM 理由生成）
- [ ] 主动营销（基于用户行为的主动触达）
- [ ] 质检系统（自动评估客服对话质量）
- [ ] 人工坐席工作台（Agent 辅助人工回复）

### 9.3 长期（v1.0+）

- [ ] 端到端语音客服
- [ ] 多 Agent 协作（售前 Agent + 售后 Agent + 物流 Agent）
- [ ] 知识图谱增强检索（GraphRAG）
- [ ] 客户流失预测与挽留策略
- [ ] 全渠道统一客服中台

---

## 附录

### A. 常见问题

**Q: 为什么选择 LangGraph 而不是直接 LangChain Agent？**
A: LangGraph 提供显式的状态管理和流程控制，适合多步骤、有分支的客服场景。LangChain Agent 的 ReAct 模式在复杂流程中容易失控。

**Q: RAG 检索效果不好怎么办？**
A: 按优先级排查：① 文档分块策略是否合理 ② Embedding 模型是否匹配语种 ③ 是否需要混合检索（BM25+向量） ④ 是否需要引入重排序模型。

**Q: 如何控制 LLM 成本？**
A: ① 对高频简单问题做缓存（Redis） ② 意图识别用小模型 ③ 非核心场景用 DeepSeek 等低成本模型 ④ 设置 token 预算上限。

### B. 参考资料

- [LangGraph 官方文档](https://langchain-ai.github.io/langgraph/)
- [LangChain RAG 教程](https://python.langchain.com/docs/tutorials/rag/)
- [ChromaDB 使用指南](https://docs.trychroma.com/)
- [FastAPI WebSocket 文档](https://fastapi.tiangolo.com/advanced/websockets/)
- [BGE-M3 Embedding 模型](https://huggingface.co/BAAI/bge-m3)
