/**
 * components/chat/MessageBubble.tsx
 * ---------------------------------
 * 单条消息气泡组件。
 *
 * ## 视觉区分
 * - **用户消息**：右对齐 (flex-row-reverse)，蓝底白字，圆角侧重右下
 * - **客服消息**：左对齐，灰底黑字，圆角侧重左上
 *
 * ## Props
 * @param role    - 'user' | 'assistant'，决定对齐方向与配色
 * @param content - 消息文本（支持 whitespace-pre-wrap 保留换行）
 */

interface MessageBubbleProps {
  /** 发送者角色 */
  role: 'user' | 'assistant';
  /** 消息正文 */
  content: string;
}

export default function MessageBubble({ role, content }: MessageBubbleProps) {
  const isUser = role === 'user';

  return (
    <div className={`flex gap-3 ${isUser ? 'flex-row-reverse' : ''}`}>
      {/* 头像圆圈 */}
      <div
        className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold ${
          isUser
            ? 'bg-blue-100 text-blue-600'   // 用户：浅蓝底深蓝字
            : 'bg-gray-100 text-gray-600'    // 客服：浅灰底灰字
        }`}
      >
        {isUser ? 'U' : 'A'}
      </div>

      {/* 消息文本气泡 */}
      <div
        className={`max-w-[75%] rounded-2xl px-4 py-3 whitespace-pre-wrap text-sm leading-relaxed ${
          isUser
            ? 'bg-blue-600 text-white rounded-tr-md'    // 用户气泡
            : 'bg-gray-100 text-gray-800 rounded-tl-md' // 客服气泡
        }`}
      >
        {content}
      </div>
    </div>
  );
}
