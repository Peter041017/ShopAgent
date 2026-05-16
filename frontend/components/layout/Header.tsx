import Link from 'next/link';

export default function Header() {
  return (
    <header className="bg-white border-b border-gray-200">
      <div className="max-w-5xl mx-auto px-4 h-14 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center text-white font-bold text-sm">
            S
          </div>
          <span className="font-semibold text-gray-900">ShopAgent 智能客服</span>
        </div>
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
