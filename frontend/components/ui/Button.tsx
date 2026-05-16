'use client';

interface ButtonProps {
  children: React.ReactNode;
  onClick?: () => void;
  disabled?: boolean;
  type?: 'button' | 'submit';
  variant?: 'primary' | 'secondary';
}

export default function Button({
  children,
  onClick,
  disabled,
  type = 'button',
  variant = 'primary',
}: ButtonProps) {
  const base = 'px-4 py-2 rounded-lg font-medium transition-colors duration-200 disabled:opacity-50';
  const styles = {
    primary: 'bg-blue-600 text-white hover:bg-blue-700 disabled:hover:bg-blue-600',
    secondary: 'bg-gray-200 text-gray-700 hover:bg-gray-300',
  };

  return (
    <button
      type={type}
      onClick={onClick}
      disabled={disabled}
      className={`${base} ${styles[variant]}`}
    >
      {children}
    </button>
  );
}
