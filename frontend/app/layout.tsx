/**
 * app/layout.tsx
 * --------------
 * Next.js App Router 根布局 —— 所有页面的 HTML 外壳。
 *
 * ## 职责
 * - 设置页面元数据（title / description，SEO 相关）
 * - 声明全局语言 (zh-CN)
 * - 应用全局背景色 (bg-gray-50)
 * - 挂载子页面内容 (children)
 */

import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'ShopAgent - 智能电商客服',
  description: 'AI 驱动的智能电商客服系统',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="zh-CN">
      <body className="bg-gray-50 min-h-screen">{children}</body>
    </html>
  );
}
