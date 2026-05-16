/**
 * components/chat/ChatInput.tsx
 * -----------------------------
 * 聊天输入区域 —— 自适应高度的多行文本输入框 + 发送按钮。
 *
 * ## 交互行为
 * - **Enter** 发送消息
 * - **Shift + Enter** 换行
 * - **发送按钮** 仅在输入非空且未禁用时可用
 * - **disabled 状态**：正在等待回复时输入框和按钮均禁用
 *
 * ## 自适应高度
 * textarea 默认显示 1 行 (rows=1)，通过监听 text 变化动态调整 height：
 * scrollHeight 不超过 150px（约 5 行），超出后内部滚动。
 *
 * @param onSend   - 消息发送回调（由 ChatContainer 注入）
 * @param disabled - 是否禁用输入（回复生成中时为 true）
 */

'use client';

import { useState, useRef, useEffect } from 'react';

interface ChatInputProps {
  /** 消息发送回调，传入用户输入的文本 */
  onSend: (message: string) => void;
  /** 是否禁用输入（等待客服回复时禁用） */
  disabled: boolean;
}

export default function ChatInput({ onSend, disabled }: ChatInputProps) {
  const [text, setText] = useState('');
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // ── 自适应高度 ─────────────────────────────────────────
  // 每次 text 变化时重新计算 textarea 高度，最大 150px
  useEffect(() => {
    if (textareaRef.current) {
      // 先重置为 auto 以获取真实 scrollHeight
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${Math.min(
        textareaRef.current.scrollHeight,
        150
      )}px`;
    }
  }, [text]);

  // ── 发送逻辑 ───────────────────────────────────────────
  const handleSubmit = () => {
    const trimmed = text.trim();
    if (!trimmed || disabled) return;
    onSend(trimmed);
    setText(''); // 发送后清空输入框
  };

  // ── 键盘处理 ───────────────────────────────────────────
  const handleKeyDown = (e: React.KeyboardEvent) => {
    // Enter（不按 Shift）→ 发送
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault(); // 阻止默认换行
      handleSubmit();
    }
    // Shift + Enter → 默认行为（换行），无需处理
  };

  // ── 渲染 ───────────────────────────────────────────────
  return (
    <div className="flex gap-2 items-end p-4 border-t border-gray-200 bg-white">
      <textarea
        ref={textareaRef}
        value={text}
        onChange={(e) => setText(e.target.value)}
        onKeyDown={handleKeyDown}
        placeholder="输入消息，Enter 发送，Shift+Enter 换行..."
        disabled={disabled}
        rows={1}
        className="flex-1 resize-none px-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:bg-gray-50 text-sm"
      />
      <button
        onClick={handleSubmit}
        disabled={disabled || !text.trim()}
        className="px-5 py-3 bg-blue-600 text-white rounded-xl font-medium hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed text-sm"
      >
        {disabled ? '...' : '发送'}
      </button>
    </div>
  );
}
