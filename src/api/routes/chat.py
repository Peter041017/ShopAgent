import re
import uuid

from fastapi import APIRouter, HTTPException, Request, WebSocket, WebSocketDisconnect
from langchain_core.messages import HumanMessage

from src.api.schemas import ChatRequest, ChatResponse
from src.utils.security import screen_user_text

router = APIRouter()

# 匹配意图路由 JSON 模式（用于从流式输出中过滤泄漏的 intent_router 输出）
_INTENT_JSON_PATTERN = re.compile(
    r'^\s*\{[\s\S]*?"intent"[\s\S]*?"slots"[\s\S]*?\}\s*',
    re.MULTILINE,
)


def _strip_intent_json(text: str) -> str:
    """移除意外泄漏到最终输出中的意图路由 JSON。"""
    return _INTENT_JSON_PATTERN.sub("", text, count=1).strip()


@router.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest, request: Request):
    ok, reason = screen_user_text(req.message)
    if not ok:
        raise HTTPException(status_code=400, detail=reason)

    agent = request.app.state.agent
    session_id = req.session_id or str(uuid.uuid4())
    config = {"configurable": {"thread_id": session_id, "user_id": req.user_id}}

    # 显式重置可能从 MemorySaver 缓存中遗留的旧值，避免状态泄漏
    result = await agent.ainvoke(
        {
            "messages": [HumanMessage(content=req.message)],
            "user_id": req.user_id,
            "session_id": session_id,
            "final_response": "",
            "_security_blocked": False,
        },
        config=config,
    )
    raw_reply = result.get("final_response") or "抱歉，我暂时无法处理您的问题"
    clean_reply = _strip_intent_json(raw_reply)
    return ChatResponse(
        session_id=session_id,
        reply=clean_reply,
        intent=result.get("intent"),
        needs_human=bool(result.get("needs_human", False)),
    )


@router.websocket("/ws/chat")
async def websocket_chat(websocket: WebSocket):
    """WebSocket 端点，支持流式输出（匹配开发文档 6.7 节）。"""
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_json()
            agent = websocket.app.state.agent
            session_id = data.get("session_id") or str(uuid.uuid4())
            user_id = data.get("user_id") or "guest"
            config = {"configurable": {"thread_id": session_id, "user_id": user_id}}
            msg = data.get("message") or ""

            # 检查是否请求流式输出
            use_stream = data.get("stream", True)

            if use_stream:
                # 流式调用 —— 用 astream_events 逐 token 推送。
                # 注意：graph 中有多个节点调用 LLM（intent_router、response_gen），
                # 只捕获 response_gen 节点的输出，避免 intent_router 的 JSON 泄漏到结果中。
                full = ""
                async for event in agent.astream_events(
                    {
                        "messages": [HumanMessage(content=msg)],
                        "user_id": user_id,
                        "session_id": session_id,
                        "final_response": "",
                        "_security_blocked": False,
                    },
                    config=config,
                    version="v2",
                ):
                    if event["event"] == "on_chat_model_stream":
                        metadata = event.get("metadata") or {}
                        node = metadata.get("langgraph_node")
                        # 只保留 response_gen 节点的 token；
                        # node 为 None 时也跳过（部分 LangGraph 版本 metadata 不完整）
                        if node != "response_gen":
                            continue
                        chunk = event["data"]["chunk"]
                        content = chunk.content if hasattr(chunk, "content") else str(chunk)
                        if content:
                            full += content
                            await websocket.send_json({"type": "token", "content": content})

                # 去除可能泄漏的 intent_router JSON
                clean = _strip_intent_json(full)
                await websocket.send_json({
                    "type": "message",
                    "content": clean,
                    "session_id": session_id,
                })
                await websocket.send_json({"type": "done"})
            else:
                # 非流式调用
                result = await agent.ainvoke(
                    {
                        "messages": [HumanMessage(content=msg)],
                        "user_id": user_id,
                        "session_id": session_id,
                        "final_response": "",
                        "_security_blocked": False,
                    },
                    config=config,
                )
                raw_reply = result.get("final_response") or ""
                clean_reply = _strip_intent_json(raw_reply)
                await websocket.send_json(
                    {
                        "type": "message",
                        "content": clean_reply,
                        "intent": result.get("intent"),
                        "session_id": session_id,
                    }
                )
                await websocket.send_json({"type": "done"})
    except WebSocketDisconnect:
        pass
