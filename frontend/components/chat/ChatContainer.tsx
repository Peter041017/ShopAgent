/**
 * components/chat/ChatContainer.tsx
 * ---------------------------------
 * 聊天容器 —— 前端消息管理的顶层组件。
 *
 * ## 职责
 * 1. **会话持久化**：通过 localStorage 维持 sessionId / userId，刷新不丢失
 * 2. **WebSocket 长连接管理**：组件挂载时建立 WS 连接，卸载时断开
 * 3. **流式渲染**：实时接收 token 并更新 UI，用户感知为"逐字输出"
 * 4. **HTTP 降级**：WS 不可用时自动切换为 HTTP POST 方式
 *
 * ## 数据流（WebSocket 路径）
 * ```
 * 用户输入 → sendMessage()
 *   → wsRef.send()
 *   → onToken(token)     → pendingContent += token   → 实时追加到气泡
 *   → onToken(token)     → pendingContent += token   → ...
 *   → onFullMessage(msg)  → pendingContent = msg      → 替换整个气泡（去重！）
 *   → onDone()           → 重置状态，本轮结束
 * ```
 * 注意：onToken 用 += 追加，onFullMessage 用 = 替换。
 * 如果 onFullMessage 也用 += 追加，会导致内容重复（累积的 token + 完整文本 = 双份）。
 *
 * ## 流式渲染关键状态
 * - `pendingContent` (ref)：本轮已累积的全部 token 文本
 * - `streamingMsgIdx` (ref)：当前正在流式写入的消息气泡在 messages 数组中的索引
 * - `hasStreamStarted` (ref)：是否已收到首个 token（控制 TypingIndicator 显隐）
 * - `isLoading` (state)：是否正在等待回复（控制输入框禁用 + 空状态时 TypingIndicator）
 *
 * ## 流式渲染时序
 * 1. 用户点击发送 → 插入 UserMessage → isLoading=true → hasStreamStarted=false
 * 2. 首个 token 到达 → hasStreamStarted=true → TypingIndicator 消失 → 插入 Assistant 气泡 → 逐 token 追加
 * 3. 后续 token → 持续追加到同一个 Assistant 气泡
 * 4. onDone → pendingContent='', streamingMsgIdx=-1, isLoading=false
 */

'use client';

import { useState, useCallback, useEffect, useRef } from 'react';
import MessageList from './MessageList';
import ChatInput from './ChatInput';
import { Message } from '@/lib/types';
import { sendChatMessage } from '@/lib/api';
import { ChatWebSocket } from '@/lib/websocket';
import { DEFAULT_USER_ID, STORAGE_SESSION_KEY } from '@/lib/constants';

// ── 会话管理工具函数 ────────────────────────────────────

/**
 * 获取或创建 sessionId。
 * 优先从 localStorage 读取，不存在则生成新 ID 并持久化。
 * sessionId 用于后端 MemorySaver 关联多轮对话上下文。
 */
function getSessionId(): string {
  if (typeof window === 'undefined') return '';
  let sid = localStorage.getItem(STORAGE_SESSION_KEY);
  if (!sid) {
    // 格式：session_<时间戳>_<6位随机字符>
    sid = `session_${Date.now()}_${Math.random().toString(36).slice(2, 8)}`;
    localStorage.setItem(STORAGE_SESSION_KEY, sid);
  }
  return sid;
}

/**
 * 获取 userId。
 * 从 localStorage 读取，不存在则使用默认用户 ID。
 */
function getUserId(): string {
  if (typeof window === 'undefined') return DEFAULT_USER_ID;
  let uid = localStorage.getItem('shopagent_user_id');
  if (!uid) {
    uid = DEFAULT_USER_ID;
    localStorage.setItem('shopagent_user_id', uid);
  }
  return uid;
}

// ── 主组件 ──────────────────────────────────────────────

export default function ChatContainer() {
  // ── 状态 ─────────────────────────────────────────────
  /** 消息列表（用户 + 客服，驱动 MessageList 渲染） */
  const [messages, setMessages] = useState<Message[]>([]);
  /** 是否正在等待客服回复 */
  const [isLoading, setIsLoading] = useState(false);
  /** 当前是否使用 WebSocket（WS 报错后切换为 false，启用 HTTP fallback） */
  const [useWs, setUseWs] = useState(true);

  // ── Ref ──────────────────────────────────────────────
  /** 会话 ID（持久化在 localStorage 中，不触发 re-render） */
  const sessionId = useRef(getSessionId());
  /** 用户 ID（持久化在 localStorage 中） */
  const userId = useRef(getUserId());
  /** ChatWebSocket 实例引用 */
  const wsRef = useRef<ChatWebSocket | null>(null);
  /** 本轮流式累积的全部 token 文本（实时拼接用） */
  const pendingContent = useRef('');
  /** 当前流式消息在 messages 数组中的索引（-1 表示无活跃流式消息） */
  const streamingMsgIdx = useRef<number>(-1);
  /** 流式已收到至少一个 token → 隐藏 TypingIndicator 并显示消息气泡 */
  const hasStreamStarted = useRef(false);

  // ── WebSocket 生命周期 ───────────────────────────────

  /**
   * 组件挂载 / useWs 变化时建立 WS 长连接。
   * 组件卸载时主动断开（intentionalClose=true，不触发重连）。
   *
   * 注意：useWs 初始为 true，WS 报错后 onError 将其置为 false，
   * 触发 useEffect cleanup → disconnect，然后 useWs=false 跳过重连。
   */
  useEffect(() => {
    if (!useWs) return;

    // ── onToken：收到流式 token → 追加模式 ────────────
    const onToken = (content: string) => {
      // 首个 token 到达 → 标记流式已开始（隐藏 TypingIndicator）
      if (!hasStreamStarted.current) {
        hasStreamStarted.current = true;
      }

      // 追加到累积缓冲区（关键：用 += 而非 =）
      pendingContent.current += content;

      // 实时更新消息列表（函数式 setState 避免闭包陷阱）
      setMessages((prev) => {
        const copy = [...prev];
        const idx = streamingMsgIdx.current;

        if (idx >= 0 && idx < copy.length) {
          // 已存在流式气泡 → 更新其内容
          copy[idx] = {
            ...copy[idx],
            content: pendingContent.current,
          };
        } else {
          // 首次 token → 创建新的 Assistant 气泡
          streamingMsgIdx.current = copy.length;
          copy.push({
            role: 'assistant' as const,
            content: pendingContent.current,
            timestamp: new Date().toISOString(),
          });
        }
        return copy;
      });
    };

    // ── onFullMessage：收到完整消息 → 替换模式 ────────
    // 修复消息重复 bug：后端流式结束后会发送 type:"message" 包含完整文本，
    // 如果还用 += 追加到已累积的 token 后面，会导致内容翻倍。
    // 因此这里用 = 直接替换。
    const onFullMsg = (content: string) => {
      // 替换而非追加
      pendingContent.current = content;

      // 更新气泡（逻辑与 onToken 一致，只是 pendingContent 已经是最终值）
      setMessages((prev) => {
        const copy = [...prev];
        const idx = streamingMsgIdx.current;

        if (idx >= 0 && idx < copy.length) {
          copy[idx] = {
            ...copy[idx],
            content: pendingContent.current,
          };
        } else {
          // 流式无 token 直接收到完整消息时（非流式模式走 else 分支，这里兜底）
          streamingMsgIdx.current = copy.length;
          copy.push({
            role: 'assistant' as const,
            content: pendingContent.current,
            timestamp: new Date().toISOString(),
          });
        }
        return copy;
      });
    };

    // ── onDone：本轮流式结束 ───────────────────────────
    const onDone = () => {
      pendingContent.current = '';
      streamingMsgIdx.current = -1;
      hasStreamStarted.current = false;
      setIsLoading(false);
    };

    // ── onError：WS 彻底失败 → 切换 HTTP 降级 ─────────
    const onError = (error: string) => {
      console.warn('WebSocket error, falling back to HTTP:', error);
      setUseWs(false);  // 切换后 useEffect cleanup 断开 WS
      setIsLoading(false);
    };

    // 创建长连接（传入 4 个回调：token / fullMessage / done / error）
    wsRef.current = new ChatWebSocket(onToken, onFullMsg, onDone, onError);
    wsRef.current.connect(sessionId.current, userId.current);

    // cleanup：组件卸载或 useWs 变为 false 时断开
    return () => {
      wsRef.current?.disconnect();
      wsRef.current = null;
    };
  }, [useWs]);

  // ── 发送消息 ─────────────────────────────────────────

  /**
   * 用户点击发送按钮或按 Enter 时触发。
   * 1. 将用户消息立即插入消息列表
   * 2. 如有 WS：通过 wsRef.send() 发送
   * 3. 如无 WS (HTTP fallback)：通过 fetch POST 发送
   */
  const sendMessage = useCallback(
    async (text: string) => {
      // ① 插入用户消息
      const userMsg: Message = {
        role: 'user',
        content: text,
        timestamp: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, userMsg]);

      // ② 进入加载状态，重置流式缓存
      setIsLoading(true);
      pendingContent.current = '';
      streamingMsgIdx.current = -1;
      hasStreamStarted.current = false;

      if (useWs && wsRef.current) {
        // ── WebSocket 路径 ──────────────────────────
        wsRef.current.send(text, sessionId.current, userId.current);
      } else {
        // ── HTTP 降级路径 ───────────────────────────
        try {
          const result = await sendChatMessage(
            userId.current,
            text,
            sessionId.current
          );
          setIsLoading(false);
          const reply: Message = {
            role: 'assistant',
            content: result.reply,
            timestamp: new Date().toISOString(),
          };
          setMessages((prev) => [...prev, reply]);
        } catch (err) {
          setIsLoading(false);
          const errMsg: Message = {
            role: 'assistant',
            content: '抱歉，暂时无法连接到客服系统，请稍后重试。',
            timestamp: new Date().toISOString(),
          };
          setMessages((prev) => [...prev, errMsg]);
        }
      }
    },
    [useWs]
  );

  // ── 渲染 ─────────────────────────────────────────────

  return (
    <div className="flex flex-col h-full bg-white rounded-xl shadow-sm border border-gray-200">
      {/* 消息列表（含自动滚动 + 空状态引导） */}
      <MessageList
        messages={messages}
        isLoading={isLoading && !hasStreamStarted.current}
      />
      {/* 输入区域（底部固定） */}
      <ChatInput onSend={sendMessage} disabled={isLoading} />
    </div>
  );
}
