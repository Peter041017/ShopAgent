export default function AdminPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">管理面板</h1>
        <p className="text-sm text-gray-500 mt-1">ShopAgent 系统管理</p>
      </div>

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

      <div className="bg-white rounded-xl border border-gray-200">
        <div className="px-6 py-4 border-b border-gray-200">
          <h2 className="font-semibold text-gray-900">最近会话</h2>
        </div>
        <div className="p-6 text-sm text-gray-500 text-center">
          会话记录功能开发中...
        </div>
      </div>

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
          <div className="mt-4 text-xs text-gray-400">
            运行 python scripts/build_index.py 更新知识索引
          </div>
        </div>
      </div>
    </div>
  );
}
