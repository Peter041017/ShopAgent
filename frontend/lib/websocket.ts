/**
 * frontend/lib/websocket.ts
 * -------------------------
 * WebSocket 长连接客户端 —— 与前端的核心通信通道。
 *
 * ## 设计要点
 *
 * 1. **单连接复用**：整个组件生命周期内维持一条 WS 连接，
 *    所有消息通过同一连接发送/接收，避免频繁握手开销。
 *
 * 2. **流式渲染**：后端逐 token 推送（type: "token"），
 *    前端实时拼接并更新消息气泡，用户感知为"逐字输出"。
 *
 * 3. **自动重连**：连接意外断开时自动重试（最多 3 次，间隔 1s），
 *    主动 disconnect 时跳过重连，避免组件卸载后还尝试恢复。
 *
 * 4. **消息排队**：连接建立中发送的消息暂存队列，onopen 后批量发送，
 *    不丢失用户输入。
 *
 * ## 协议（与后端 src/api/routes/chat.py 对应）
 *
 * 客户端 → 服务端: JSON { message, session_id, user_id }
 * 服务端 → 客户端: JSON { type: "token"|"message"|"done", content?, ... }
 */

import { WSMessage, WSRequest } from '@/lib/types';
import { WS_URL } from '@/lib/constants';

// ── 常量 ────────────────────────────────────────────────────

/** 连接断开后最大重连次数 */
const MAX_RECONNECT_ATTEMPTS = 3;
/** 重连间隔（毫秒） */
const RECONNECT_DELAY_MS = 1000;

// ── 主类 ────────────────────────────────────────────────────

export class ChatWebSocket {
  /** 原生 WebSocket 实例 */
  private ws: WebSocket | null = null;
  /** WebSocket 服务端地址（含路径） */
  private url: string;

  // 回调函数（构造时注入，解耦 UI 层与通信层）
  /**
   * token 回调 —— 流式输出时逐 token 调用，ChatContainer 会 **追加** 到累积缓冲区。
   * 对应服务端 type: "token" 事件。
   */
  private onToken: (content: string) => void;
  /**
   * 完整消息回调 —— 流式输出结束后调用，ChatContainer 会 **替换** 整个消息内容。
   * 这是修复消息重复 bug 的关键：type: "message" 携带的是已累积的完整文本，
   * 如果还用 onToken 追加就会导致内容翻倍。
   * 对应服务端 type: "message" 事件。
   */
  private onFullMessage: (content: string) => void;
  /** 本轮对话结束的回调 */
  private onDone: () => void;
  /** 连接错误（重连耗尽）时的回调 */
  private onError: (error: string) => void;

  // 待发送队列与会话元信息
  /** 连接建立中积压的待发送消息 */
  private pendingMessages: WSRequest[] = [];
  /** 当前会话 ID */
  private sessionId = '';
  /** 当前用户 ID */
  private userId = '';

  // 重连控制
  /** 已重连次数 */
  private reconnectAttempts = 0;
  /** 重连延时器句柄 */
  private reconnectTimer: ReturnType<typeof setTimeout> | null = null;
  /** 是否为主动关闭（主动断开不触发重连） */
  private intentionalClose = false;

  // ── 构造函数 ──────────────────────────────────────────

  /**
   * @param onToken      - 收到流式 token 时的回调（追加模式）
   * @param onFullMessage - 收到完整消息时的回调（替换模式）
   * @param onDone       - 本轮流式输出结束的回调
   * @param onError      - 连接彻底失败时的回调（触发 HTTP fallback）
   */
  constructor(
    onToken: (content: string) => void,
    onFullMessage: (content: string) => void,
    onDone: () => void,
    onError: (error: string) => void
  ) {
    this.url = `${WS_URL}/api/v1/ws/chat`;
    this.onToken = onToken;
    this.onFullMessage = onFullMessage;
    this.onDone = onDone;
    this.onError = onError;
  }

  // ── 公开方法 ──────────────────────────────────────────

  /**
   * 建立 WebSocket 连接。
   * 组件挂载时调用一次，整个生命周期复用同一条连接。
   *
   * @param sessionId - 会话标识（从 localStorage 读取或新建）
   * @param userId    - 用户标识
   */
  connect(sessionId: string, userId: string) {
    this.sessionId = sessionId;
    this.userId = userId;
    this.intentionalClose = false;
    this._createSocket();
  }

  /**
   * 发送聊天消息。
   * - 连接已就绪：直接发送
   * - 连接建立中：加入待发送队列，onopen 后自动发送
   * - 连接断开：触发重连并将消息加入队列
   *
   * @param text      - 用户输入的文本
   * @param sessionId - 会话 ID
   * @param userId    - 用户 ID
   */
  send(text: string, sessionId: string, userId: string) {
    const msg: WSRequest = { message: text, session_id: sessionId, user_id: userId };

    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      // 连接就绪 → 直接发送
      this.ws.send(JSON.stringify(msg));
    } else if (this.ws && this.ws.readyState === WebSocket.CONNECTING) {
      // 正在连接 → 入队等待
      this.pendingMessages.push(msg);
    } else {
      // 连接已断开 → 触发重连 + 入队
      this.sessionId = sessionId;
      this.userId = userId;
      this.pendingMessages.push(msg);
      this._createSocket();
    }
  }

  /**
   * 主动断开连接（组件卸载时调用）。
   * 设置 intentionalClose 标志阻止自动重连。
   */
  disconnect() {
    this.intentionalClose = true;
    // 清理重连定时器
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer);
      this.reconnectTimer = null;
    }
    // 关闭 WebSocket
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
    // 清空待发送队列（组件已卸载，消息无意义）
    this.pendingMessages = [];
  }

  // ── 内部方法 ──────────────────────────────────────────

  /**
   * 创建原生 WebSocket 连接并绑定事件处理。
   * - onopen:   重置重连计数，发送积压消息
   * - onmessage: 解析服务端推送，按 type 分发到对应回调
   * - onerror:   静默（onclose 也会触发，错误处理集中在 onclose）
   * - onclose:   非主动关闭时尝试重连
   */
  private _createSocket() {
    // 清理旧连接（解除事件绑定，避免内存泄漏和重复回调）
    if (this.ws) {
      this.ws.onopen = null;
      this.ws.onmessage = null;
      this.ws.onerror = null;
      this.ws.onclose = null;
      if (
        this.ws.readyState === WebSocket.OPEN ||
        this.ws.readyState === WebSocket.CONNECTING
      ) {
        this.ws.close();
      }
    }

    try {
      this.ws = new WebSocket(this.url);

      // ── 连接成功 ───────────────────────────────────
      this.ws.onopen = () => {
        this.reconnectAttempts = 0; // 重置重连计数
        // 发送所有积压消息（连接建立期间用户可能已输入多条）
        for (const msg of this.pendingMessages) {
          this.ws?.send(JSON.stringify(msg));
        }
        this.pendingMessages = [];
      };

      // ── 收到消息 ───────────────────────────────────
      this.ws.onmessage = (event) => {
        try {
          const data: WSMessage = JSON.parse(event.data);

          if (data.type === 'token' && data.content) {
            // 流式 token → 追加模式（onToken 做 +=）
            this.onToken(data.content);
          } else if (data.type === 'message' && data.content) {
            // 完整消息 → 替换模式（onFullMessage 做 =，避免与累积的 token 重复）
            this.onFullMessage(data.content);
          } else if (data.type === 'done') {
            // 本轮结束 → 重置流式状态
            this.onDone();
          }
        } catch {
          // 解析失败时尝试当纯文本显示（兜底，走追加模式）
          this.onToken(event.data);
        }
      };

      // ── 连接错误 ───────────────────────────────────
      // 注意：onerror 不提供具体错误信息，仅作占位；
      // 实际的重连/降级逻辑在 onclose 中处理。
      this.ws.onerror = () => {};

      // ── 连接关闭 ───────────────────────────────────
      this.ws.onclose = () => {
        if (!this.intentionalClose && this.reconnectAttempts < MAX_RECONNECT_ATTEMPTS) {
          // 非主动关闭且未超重连次数 → 延时重连
          this.reconnectAttempts++;
          this.reconnectTimer = setTimeout(
            () => this._createSocket(),
            RECONNECT_DELAY_MS
          );
        } else if (!this.intentionalClose) {
          // 重连耗尽 → 通知上层切换为 HTTP fallback
          this.onError('WebSocket connection lost');
        }
      };
    } catch {
      // new WebSocket() 抛出异常（如 URL 格式错误）
      this.onError('Failed to create WebSocket connection');
    }
  }
}
