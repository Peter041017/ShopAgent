/**
 * components/layout/Header.tsx
 * ----------------------------
 * 顶部导航栏 —— 全站共享的页面头部。
 *
 * ## 布局
 * - 左侧：Logo + "ShopAgent 智能客服" 标题
 * - 右侧：导航链接（聊天 / 管理）
 *
 * ## 路由
 * - "/"       → 聊天页 (page.tsx)
 * - "/admin"  → 管理面板 (admin/page.tsx)
 */

import Link from 'next/link';

export default function Header() {
  return (
    <header className="bg-white border-b border-gray-200">
      <div className="max-w-5xl mx-auto px-4 h-14 flex items-center justify-between">
        {/* ── 左侧品牌 ──────────────────────────────── */}
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center text-white font-bold text-sm">
            S
          </div>
          <span className="font-semibold text-gray-900">ShopAgent 智能客服</span>
        </div>

        {/* ── 右侧导航 ──────────────────────────────── */}
        <nav className="flex items-center gap-4 text-sm">
          <Link href="/" className="text-gray-600 hover:text-gray-900">
            聊天
          </Link>
          <Link href="/admin" className="text-gray-600 hover:text-gray-900">
            管理
          </Link>
        </nav>
      </div>
    </header>
  );
}
