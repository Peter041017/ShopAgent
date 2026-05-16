/**
 * frontend/lib/types.ts
 * ---------------------
 * 前端全局类型定义。
 * 与后端 Pydantic schemas (src/api/schemas.py) 保持结构对齐。
 */

// ── 聊天消息 ────────────────────────────────────────────────

/** 单条对话消息，用于渲染消息列表 */
export interface Message {
  /** 发送者角色：user=用户, assistant=AI 客服 */
  role: 'user' | 'assistant';
  /** 消息正文（支持纯文本，后续可扩展 Markdown） */
  content: string;
  /** ISO 8601 时间戳，用于排序与展示 */
  timestamp: string;
}

// ── HTTP API 类型 ───────────────────────────────────────────

/** POST /api/v1/chat 的响应体 */
export interface ChatResponse {
  /** 会话 ID（首次请求后端自动生成，后续携带以保持上下文） */
  session_id: string;
  /** 客服回复的文本内容 */
  reply: string;
  /** 意图分类结果（可为 null） */
  intent: string | null;
  /** 是否需要转人工 */
  needs_human: boolean;
}

// ── WebSocket 消息类型 ──────────────────────────────────────

/** 服务端 → 客户端 WebSocket 推送的单条消息 */
export interface WSMessage {
  /** 消息类型：
   *   token   — 流式输出的单个 token（前端实时拼接）
   *   message — 单条完整消息（流式结束后或非流式模式）
   *   done    — 本轮对话结束信号 */
  type: 'token' | 'message' | 'done';
  /** 消息文本（token/message 类型时有值） */
  content?: string;
  /** 意图分类（message 类型时附带） */
  intent?: string;
  /** 会话 ID */
  session_id?: string;
}

/** 客户端 → 服务端 WebSocket 发送的请求体 */
export interface WSRequest {
  /** 用户输入的文本 */
  message: string;
  /** 会话 ID */
  session_id: string;
  /** 用户标识 */
  user_id: string;
}
