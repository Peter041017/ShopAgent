import uuid

from fastapi import APIRouter, HTTPException, Request, WebSocket, WebSocketDisconnect
from langchain_core.messages import HumanMessage

from src.api.schemas import ChatRequest, ChatResponse
from src.utils.security import screen_user_text

router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest, request: Request):
    ok, reason = screen_user_text(req.message)
    if not ok:
        raise HTTPException(status_code=400, detail=reason)

    agent = request.app.state.agent
    session_id = req.session_id or str(uuid.uuid4())
    config = {"configurable": {"thread_id": session_id, "user_id": req.user_id}}

    result = await agent.ainvoke(
        {
            "messages": [HumanMessage(content=req.message)],
            "user_id": req.user_id,
            "session_id": session_id,
        },
        config=config,
    )
    return ChatResponse(
        session_id=session_id,
        reply=result.get("final_response", "抱歉，我暂时无法处理您的问题"),
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
                # 流式调用 —— 用 astream_events 逐 token 推送
                full = ""
                async for event in agent.astream_events(
                    {
                        "messages": [HumanMessage(content=msg)],
                        "user_id": user_id,
                        "session_id": session_id,
                    },
                    config=config,
                    version="v2",
                ):
                    if event["event"] == "on_chat_model_stream":
                        chunk = event["data"]["chunk"]
                        content = chunk.content if hasattr(chunk, "content") else str(chunk)
                        if content:
                            full += content
                            await websocket.send_json({"type": "token", "content": content})

                # 推送完整消息和意图
                await websocket.send_json({
                    "type": "message",
                    "content": full,
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
                    },
                    config=config,
                )
                await websocket.send_json(
                    {
                        "type": "message",
                        "content": result.get("final_response", ""),
                        "intent": result.get("intent"),
                        "session_id": session_id,
                    }
                )
                await websocket.send_json({"type": "done"})
    except WebSocketDisconnect:
        pass
