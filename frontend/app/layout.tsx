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
      <body className="bg-gray-50 min-h-screen">
        {children}
      </body>
    </html>
  );
}
