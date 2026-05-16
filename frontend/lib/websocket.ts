import { WSMessage, WSRequest } from '@/lib/types';

const WS_BASE = process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000';

export class ChatWebSocket {
  private ws: WebSocket | null = null;
  private url: string;
  private onMessage: (content: string) => void;
  private onDone: () => void;
  private onError: (error: string) => void;

  constructor(
    onMessage: (content: string) => void,
    onDone: () => void,
    onError: (error: string) => void
  ) {
    this.url = `${WS_BASE}/api/v1/ws/chat`;
    this.onMessage = onMessage;
    this.onDone = onDone;
    this.onError = onError;
  }

  connect(sessionId: string, userId: string) {
    try {
      this.ws = new WebSocket(this.url);

      this.ws.onopen = () => {
        // connection established
      };

      this.ws.onmessage = (event) => {
        try {
          const data: WSMessage = JSON.parse(event.data);
          if (data.type === 'message' && data.content) {
            this.onMessage(data.content);
          } else if (data.type === 'done') {
            this.onDone();
          }
        } catch {
          this.onMessage(event.data);
        }
      };

      this.ws.onerror = () => {
        this.onError('WebSocket connection error');
      };

      this.ws.onclose = () => {
        // connection closed
      };
    } catch {
      this.onError('Failed to create WebSocket connection');
    }
  }

  send(text: string, sessionId: string, userId: string) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      const msg: WSRequest = { message: text, session_id: sessionId, user_id: userId };
      this.ws.send(JSON.stringify(msg));
    } else {
      this.onError('WebSocket is not connected');
    }
  }

  disconnect() {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
  }
}
