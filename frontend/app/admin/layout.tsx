/**
 * app/admin/layout.tsx
 * --------------------
 * 管理后台专用布局 —— 与首页共享 Header，内容区宽度更宽 (max-w-5xl)。
 *
 * 与根布局 (app/layout.tsx) 的关系：
 * - 根布局提供 HTML/body 外壳 + 全局元数据
 * - 本布局嵌套在根布局内部，添加 Header + 内容区约束
 */

import Header from '@/components/layout/Header';

export default function AdminLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="flex flex-col min-h-screen">
      <Header />
      <main className="flex-1 max-w-5xl w-full mx-auto p-4">
        {children}
      </main>
    </div>
  );
}
