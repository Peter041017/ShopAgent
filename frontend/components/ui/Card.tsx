/**
 * components/ui/Card.tsx
 * ----------------------
 * 通用卡片容器（服务端组件，无交互状态）。
 *
 * 提供统一的白色圆角边框 + 阴影外观，
 * 通过 className 透传支持外部自定义样式。
 */

interface CardProps {
  children: React.ReactNode;
  className?: string;
}

export default function Card({ children, className = '' }: CardProps) {
  return (
    <div
      className={`bg-white rounded-xl shadow-sm border border-gray-200 ${className}`}
    >
      {children}
    </div>
  );
}
