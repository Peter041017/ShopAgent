# API 概要

- `POST /api/v1/chat`：JSON 体 `{ "user_id", "session_id?", "message" }`
- `WebSocket /api/v1/ws/chat`：消息 `{ "user_id", "session_id?", "message" }`
- `GET /api/v1/admin/health`：管理健康检查
- `POST /api/v1/knowledge/reindex`：占位，实际索引用 `scripts/build_index.py`
