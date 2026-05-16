interface MessageBubbleProps {
  role: 'user' | 'assistant';
  content: string;
}

export default function MessageBubble({ role, content }: MessageBubbleProps) {
  const isUser = role === 'user';

  return (
    <div className={`flex gap-3 ${isUser ? 'flex-row-reverse' : ''}`}>
      <div
        className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold ${
          isUser ? 'bg-blue-100 text-blue-600' : 'bg-gray-100 text-gray-600'
        }`}
      >
        {isUser ? 'U' : 'A'}
      </div>
      <div
        className={`max-w-[75%] rounded-2xl px-4 py-3 whitespace-pre-wrap text-sm leading-relaxed ${
          isUser
            ? 'bg-blue-600 text-white rounded-tr-md'
            : 'bg-gray-100 text-gray-800 rounded-tl-md'
        }`}
      >
        {content}
      </div>
    </div>
  );
}
