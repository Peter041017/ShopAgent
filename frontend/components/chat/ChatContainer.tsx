'use client';

import { useState, useCallback, useEffect, useRef } from 'react';
import MessageList from './MessageList';
import ChatInput from './ChatInput';
import { Message } from '@/lib/types';
import { sendChatMessage } from '@/lib/api';
import { ChatWebSocket } from '@/lib/websocket';
import { DEFAULT_USER_ID, STORAGE_SESSION_KEY } from '@/lib/constants';

function getSessionId(): string {
  if (typeof window === 'undefined') return '';
  let sid = localStorage.getItem(STORAGE_SESSION_KEY);
  if (!sid) {
    sid = `session_${Date.now()}_${Math.random().toString(36).slice(2, 8)}`;
    localStorage.setItem(STORAGE_SESSION_KEY, sid);
  }
  return sid;
}

function getUserId(): string {
  if (typeof window === 'undefined') return DEFAULT_USER_ID;
  let uid = localStorage.getItem('shopagent_user_id');
  if (!uid) {
    uid = DEFAULT_USER_ID;
    localStorage.setItem('shopagent_user_id', uid);
  }
  return uid;
}

export default function ChatContainer() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [useWs, setUseWs] = useState(true);
  const sessionId = useRef(getSessionId());
  const userId = useRef(getUserId());
  const wsRef = useRef<ChatWebSocket | null>(null);
  const pendingContent = useRef('');

  const onWsMessage = useCallback((content: string) => {
    pendingContent.current += content;
  }, []);

  const onWsDone = useCallback(() => {
    const text = pendingContent.current;
    pendingContent.current = '';
    if (text) {
      setMessages((prev) => [
        ...prev,
        { role: 'assistant', content: text, timestamp: new Date().toISOString() },
      ]);
    }
    setIsLoading(false);
  }, []);

  const onWsError = useCallback(
    (error: string) => {
      console.warn('WebSocket error, falling back to HTTP:', error);
      setUseWs(false);
      setIsLoading(false);
    },
    []
  );

  useEffect(() => {
    return () => {
      wsRef.current?.disconnect();
    };
  }, []);

  const sendMessage = useCallback(
    async (text: string) => {
      const userMsg: Message = { role: 'user', content: text, timestamp: new Date().toISOString() };
      setMessages((prev) => [...prev, userMsg]);

      setIsLoading(true);
      pendingContent.current = '';

      if (useWs) {
        wsRef.current = new ChatWebSocket(onWsMessage, onWsDone, onWsError);
        wsRef.current.connect(sessionId.current, userId.current);
        wsRef.current.send(text, sessionId.current, userId.current);
      } else {
        try {
          const result = await sendChatMessage(userId.current, text, sessionId.current);
          setIsLoading(false);
          const reply: Message = {
            role: 'assistant',
            content: result.reply,
            timestamp: new Date().toISOString(),
          };
          setMessages((prev) => [...prev, reply]);
        } catch (err) {
          setIsLoading(false);
          const errMsg: Message = {
            role: 'assistant',
            content: '抱歉，暂时无法连接到客服系统，请稍后重试。',
            timestamp: new Date().toISOString(),
          };
          setMessages((prev) => [...prev, errMsg]);
        }
      }
    },
    [useWs, onWsMessage, onWsDone, onWsError]
  );

  return (
    <div className="flex flex-col h-full bg-white rounded-xl shadow-sm border border-gray-200">
      <MessageList messages={messages} isLoading={isLoading} />
      <ChatInput onSend={sendMessage} disabled={isLoading} />
    </div>
  );
}
