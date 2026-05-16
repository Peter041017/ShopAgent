# ShopAgent - 智能电商客服

基于 Python + LangChain + LangGraph + RAG 的智能电商客服系统，配备 Next.js 前端界面。

## 架构

```
用户 → Next.js 前端 → FastAPI (HTTP/WS) → LangGraph Agent
                              ├─ intent_router → LLM 意图识别
                              ├─ rag_retrieval → Chroma 向量检索
                              ├─ tool_executor → SQLite 数据库查询
                              ├─ clarification → 追问澄清
                              └─ response_gen → LLM 生成回复
```

## 快速开始

### 前置要求

- Python >= 3.11
- Node.js >= 18
- （可选）Docker（仅生产环境需要 Redis / PostgreSQL）

### 后端

```bash
# 安装后端依赖
pip install -e ".[dev]"

# 初始化数据库（SQLite，无需 Docker）
python scripts/init_db.py

# 构建知识库索引（可选，需要 OPENAI_API_KEY）
cp .env .env
# 编辑 .env 填入 OPENAI_API_KEY 或 DEEPSEEK_API_KEY
python scripts/build_index.py

# 启动 API 服务（任选一种）
python src/main.py              # 推荐
uvicorn src.main:app --reload   # 或用 uvicorn
python run.py                   # 或用 run.py
```

### 前端

```bash
cd frontend
npm install
npm run dev
```

打开 http://localhost:3000 开始对话。

## 默认配置

| 配置项 | 默认值 | 说明 |
|--------|--------|------|
| LLM | DeepSeek V4 Pro (deepseek-v4-pro) | 通过 OPENAI_BASE_URL 配置 |
| 向量嵌入 | text-embedding-3-small | 可单独配置 EMBEDDING_* |
| 数据库 | SQLite (data/shopagent.db) | 设置 DATABASE_URL 切换 PostgreSQL |
| 向量存储 | Chroma (data/chroma) | 文件级持久化 |

## API

- `POST /api/v1/chat` - 聊天（HTTP）
- `WS /api/v1/ws/chat` - 聊天（WebSocket）
- `GET /health` - 健康检查
- `GET /api/v1/admin/health` - 管理健康检查
- `POST /api/v1/knowledge/reindex` - 重建知识索引（占位）

## 演示场景

启动服务后，可在前端尝试以下对话：

1. **商品咨询**: "iPhone 16 Pro 有什么颜色？"
2. **订单查询**: "查询我的订单列表"
3. **物流追踪**: "查物流 SF1487654321"
4. **售后服务**: "我要退款 ORD-20260512-001"
5. **退货政策**: "退换货政策是什么？"

## Makefile 命令

```bash
make install      # 安装所有依赖（后端 + 前端）
make init-db      # 初始化数据库和种子数据
make index        # 构建知识库索引
make run          # 启动 API 服务
make frontend     # 启动前端开发服务器
make test         # 运行测试
make lint         # 代码检查（ruff）
```

## Bug 修复记录

### v0.1.1 (2026-05-16)

**1. 中文知识库关键词匹配无效** — `src/agent/nodes/rag_node.py`

原 `_tokenize()` 函数将中文按**单字**切分（如 "注册" → ["注", "册"]）。常见汉字几乎在每个文档中都能命中，导致 `_keyword_match` 得分无区分度，中文查询的回退匹配几乎随机。

修复：改为 **bigram（二元组）** 切分（"注册账户" → ["注册", "册账", "账户"]），大幅提升中文关键词匹配精度。同时修复了 `_load_knowledge_docs` 中的相对路径问题（改为基于 `__file__` 的绝对路径），确保任意工作目录下都能正确加载知识文件。

**2. 意图路由 JSON 泄漏到输出** — `src/api/routes/chat.py`, `src/agent/nodes/response_gen.py`

两个根因：
- WebSocket 流式过滤器 `if node is not None and node != "response_gen": continue` 在 `langgraph_node` 为 `None` 时放行（部分 LangGraph 版本 metadata 不完整），导致 intent_router 的 JSON token 混入流式输出
- `MemorySaver` 持久化的 `final_response` 等字段在下一轮未被覆盖时产生状态泄漏

修复：
- 流式过滤改为 `if node != "response_gen": continue`（同时拦截 `None` 节点）
- 每次调用 Agent 前显式重置 `final_response=""` 和 `_security_blocked=False`
- 在 chat API 层和 response_gen 节点层添加正则清洗函数 `_strip_intent_json()`，防御性移除可能泄漏的 JSON 模式
- response_gen 的 System Prompt 增加 "不要输出 JSON" 的明确约束

### v0.1.0 (初始版)

基础功能：意图识别 → RAG 检索 → 工具调用 → 回复生成的 LangGraph 流程。
支持的意图类型：商品咨询 (product_inquiry)、订单查询 (order_query)、
售后服务 (after_sales)、闲聊 (chitchat)、未知 (unknown)。

## 依赖

- **后端**: FastAPI, LangChain, LangGraph, SQLAlchemy (async), Chroma, aiosqlite
- **前端**: Next.js, React, TypeScript, Tailwind CSS
