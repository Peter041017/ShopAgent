from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    user_id: str = Field(..., description="用户 ID")
    session_id: str | None = Field(None, description="会话 ID，不传则新建")
    message: str = Field(..., min_length=1, description="用户消息")


class ChatResponse(BaseModel):
    session_id: str
    reply: str
    intent: str | None = None
    needs_human: bool = False
