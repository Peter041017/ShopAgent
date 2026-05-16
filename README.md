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

## 依赖

- **后端**: FastAPI, LangChain, LangGraph, SQLAlchemy (async), Chroma, aiosqlite
- **前端**: Next.js, React, TypeScript, Tailwind CSS
