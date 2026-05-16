import Header from '@/components/layout/Header';
import ChatContainer from '@/components/chat/ChatContainer';

export default function Home() {
  return (
    <div className="flex flex-col min-h-screen">
      <Header />
      <main className="flex-1 max-w-3xl w-full mx-auto p-4">
        <div className="h-[calc(100vh-7rem)]">
          <ChatContainer />
        </div>
      </main>
    </div>
  );
}
