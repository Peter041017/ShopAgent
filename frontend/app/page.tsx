/**
 * app/page.tsx
 * ------------
 * 首页 / 聊天页 —— 全屏聊天界面。
 *
 * ## 布局结构
 * ```
 * ┌────────────────────────────┐
 * │         Header             │  ← 顶部导航栏
 * ├────────────────────────────┤
 * │                            │
 * │     ChatContainer          │  ← 消息列表 + 输入框
 * │     (max-w-3xl 居中)       │
 * │                            │
 * └────────────────────────────┘
 * ```
 *
 * ChatContainer 高度 = 100vh - 7rem（Header 高度 + padding）
 */

import Header from '@/components/layout/Header';
import ChatContainer from '@/components/chat/ChatContainer';

export default function Home() {
  return (
    <div className="flex flex-col min-h-screen">
      <Header />
      <main className="flex-1 max-w-3xl w-full mx-auto p-4">
        {/* 固定高度避免页面滚动，内部 overflow-y-auto 由 MessageList 处理 */}
        <div className="h-[calc(100vh-7rem)]">
          <ChatContainer />
        </div>
      </main>
    </div>
  );
}
