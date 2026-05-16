/**
 * components/chat/MessageList.tsx
 * -------------------------------
 * 消息列表容器 —— 渲染全部对话历史 + 自动滚动到底部。
 *
 * ## 状态处理
 * - **空列表**：显示引导文案"发送消息开始与智能客服对话"
 * - **有消息**：逐条渲染 MessageBubble + 流式进行中时底部显示 TypingIndicator
 * - **新消息到达**：自动 smooth 滚动到最底部（useEffect 监听 messages/isLoading）
 *
 * ## 流式渲染流程
 * 1. 用户发送消息 → isLoading=true → 底部出现 TypingIndicator
 * 2. 首个 token 到达 → ChatContainer 中的 hasStreamStarted 变为 true
 *    → TypingIndicator 消失，Assistant 气泡开始实时追加文本
 * 3. onDone → isLoading=false → 本轮结束
 */

import { useEffect, useRef } from 'react';
import MessageBubble from './MessageBubble';
import TypingIndicator from './TypingIndicator';
import { Message } from '@/lib/types';

interface MessageListProps {
  /** 完整消息列表（用户 + 客服），只读 */
  messages: Message[];
  /** 是否正在等待回复（控制 TypingIndicator 显隐） */
  isLoading: boolean;
}

export default function MessageList({ messages, isLoading }: MessageListProps) {
  // 底部锚点 ref —— 用于自动滚动
  const bottomRef = useRef<HTMLDivElement>(null);

  // 每当消息列表或加载状态变化，平滑滚动到底部
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isLoading]);

  // ── 空状态 ─────────────────────────────────────────────
  if (messages.length === 0) {
    return (
      <div className="flex-1 flex items-center justify-center text-gray-400 text-sm">
        发送消息开始与智能客服对话
      </div>
    );
  }

  // ── 消息列表 ───────────────────────────────────────────
  return (
    <div className="flex-1 overflow-y-auto p-4 space-y-4">
      {messages.map((msg, i) => (
        <MessageBubble key={i} role={msg.role} content={msg.content} />
      ))}

      {/* 加载中且尚未收到任何 token 时显示"正在输入"动画 */}
      {isLoading && <TypingIndicator />}

      {/* 滚动锚点：始终渲染在列表末尾的不可见 div */}
      <div ref={bottomRef} />
    </div>
  );
}
