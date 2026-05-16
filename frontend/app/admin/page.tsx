/**
 * app/admin/page.tsx
 * ------------------
 * 管理仪表盘 —— 展示系统运行概况。
 *
 * ## 当前功能（v0.1）
 * - 统计卡片行：在线会话数 / 今日咨询量 / 满意率（静态演示数据）
 * - 最近会话列表（占位）
 * - 知识库状态：商品/政策/FAQ 文档数量统计 + 索引构建提示
 *
 * ## 待扩展
 * - 接入后端 ADMIN API（/api/v1/admin/health 等）
 * - 会话记录实际数据查询
 * - 知识库重新索引操作按钮
 */

export default function AdminPage() {
  return (
    <div className="space-y-6">
      {/* ── 页头 ────────────────────────────────────── */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">管理面板</h1>
        <p className="text-sm text-gray-500 mt-1">ShopAgent 系统管理</p>
      </div>

      {/* ── 统计卡片 ────────────────────────────────── */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-white rounded-xl border border-gray-200 p-6">
          <div className="text-2xl font-bold text-gray-900">4</div>
          <div className="text-sm text-gray-500 mt-1">在线会话</div>
        </div>
        <div className="bg-white rounded-xl border border-gray-200 p-6">
          <div className="text-2xl font-bold text-gray-900">10</div>
          <div className="text-sm text-gray-500 mt-1">今日咨询</div>
        </div>
        <div className="bg-white rounded-xl border border-gray-200 p-6">
          <div className="text-2xl font-bold text-gray-900">98%</div>
          <div className="text-sm text-gray-500 mt-1">满意率</div>
        </div>
      </div>

      {/* ── 最近会话（占位） ────────────────────────── */}
      <div className="bg-white rounded-xl border border-gray-200">
        <div className="px-6 py-4 border-b border-gray-200">
          <h2 className="font-semibold text-gray-900">最近会话</h2>
        </div>
        <div className="p-6 text-sm text-gray-500 text-center">
          会话记录功能开发中...
        </div>
      </div>

      {/* ── 知识库状态 ──────────────────────────────── */}
      <div className="bg-white rounded-xl border border-gray-200">
        <div className="px-6 py-4 border-b border-gray-200">
          <h2 className="font-semibold text-gray-900">知识库状态</h2>
        </div>
        <div className="p-6">
          <div className="space-y-3">
            <div className="flex items-center justify-between text-sm">
              <span className="text-gray-600">商品知识</span>
              <span className="text-gray-900 font-medium">10 个文档</span>
            </div>
            <div className="flex items-center justify-between text-sm">
              <span className="text-gray-600">政策文档</span>
              <span className="text-gray-900 font-medium">5 个文档</span>
            </div>
            <div className="flex items-center justify-between text-sm">
              <span className="text-gray-600">FAQ</span>
              <span className="text-gray-900 font-medium">5 个文档</span>
            </div>
          </div>
          {/* 索引导引提示 */}
          <div className="mt-4 text-xs text-gray-400">
            运行 python scripts/build_index.py 更新知识索引
          </div>
        </div>
      </div>
    </div>
  );
}
