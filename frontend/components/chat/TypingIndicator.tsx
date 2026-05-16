/**
 * components/chat/TypingIndicator.tsx
 * -----------------------------------
 * "正在输入"动画指示器。
 *
 * 显示时机：用户发送消息后、第一次收到 token 之前（isLoading && !hasStreamStarted）。
 * 一旦首个 token 到达，该组件即被隐藏，替换为实时的消息气泡。
 *
 * 视觉效果：三个灰色圆点依次弹跳（animationDelay 错开 150ms 间隔）。
 */

export default function TypingIndicator() {
  return (
    <div className="flex gap-3">
      {/* 头像占位（与 MessageBubble 中 AI 侧头像样式一致） */}
      <div className="flex-shrink-0 w-8 h-8 rounded-full bg-gray-100 flex items-center justify-center text-sm font-bold text-gray-600">
        A
      </div>

      {/* 动画圆点容器 */}
      <div className="bg-gray-100 rounded-2xl rounded-tl-md px-5 py-4">
        <div className="flex gap-1.5">
          <span
            className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"
            style={{ animationDelay: '0ms' }}
          />
          <span
            className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"
            style={{ animationDelay: '150ms' }}
          />
          <span
            className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"
            style={{ animationDelay: '300ms' }}
          />
        </div>
      </div>
    </div>
  );
}
