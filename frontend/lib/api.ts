/**
 * frontend/lib/api.ts
 * -------------------
 * HTTP API 客户端 —— 封装对后端 REST 接口的 fetch 调用。
 *
 * 使用场景：
 * - WebSocket 不可用时的降级方案（ChatContainer 中 useWs=false 时触发）
 * - 管理后台等非聊天场景的 API 调用
 *
 * 注意：聊天主链路优先走 WebSocket 长连接（见 websocket.ts），
 * HTTP 仅作为 fallback。
 */

import { ChatResponse } from '@/lib/types';
import { API_URL } from '@/lib/constants';

/**
 * 发送聊天消息（HTTP POST）。
 *
 * @param userId   - 用户标识
 * @param message  - 用户输入文本
 * @param sessionId - 会话 ID（可选，不传则后端自动创建）
 * @returns 包含客服回复、意图、会话 ID 的响应体
 * @throws  网络错误或非 2xx 响应时抛出异常
 */
export async function sendChatMessage(
  userId: string,
  message: string,
  sessionId?: string
): Promise<ChatResponse> {
  const res = await fetch(`${API_URL}/api/v1/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      user_id: userId,
      message,
      session_id: sessionId,
    }),
  });

  if (!res.ok) {
    const err = await res.text();
    throw new Error(`API error ${res.status}: ${err}`);
  }

  return res.json();
}
