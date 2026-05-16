/**
 * frontend/lib/constants.ts
 * -------------------------
 * 全局配置常量。所有环境相关配置通过 NEXT_PUBLIC_* 环境变量注入，
 * 未设置时回退到本地开发默认值。
 */

/** 后端 HTTP API 基地址 */
export const API_URL =
  process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

/** 后端 WebSocket 基地址（注意 ws:// 协议） */
export const WS_URL =
  process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000';

/** 默认用户 ID（演示/开发用，生产环境应接入真实用户系统） */
export const DEFAULT_USER_ID = 'user_001';

/** localStorage 中存储 sessionId 的键名 */
export const STORAGE_SESSION_KEY = 'shopagent_session_id';
