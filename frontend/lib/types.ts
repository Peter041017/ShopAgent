export interface Message {
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
}

export interface ChatResponse {
  session_id: string;
  reply: string;
  intent: string | null;
  needs_human: boolean;
}

export interface WSMessage {
  type: 'message' | 'done';
  content?: string;
  intent?: string;
  session_id?: string;
}

export interface WSRequest {
  message: string;
  session_id: string;
  user_id: string;
}
