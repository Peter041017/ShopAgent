from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.agent.graph import create_agent
from src.api.middleware import RateLimitMiddleware, RequestLoggingMiddleware
from src.api.routes import admin, chat, knowledge
from src.database.engine import init_db
from src.utils.logger import setup_logging


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging()
    await init_db()
    app.state.agent = create_agent()
    yield


app = FastAPI(
    title="ShopAgent - 智能电商客服",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(RateLimitMiddleware, max_requests=60, window_seconds=60)
app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat.router, prefix="/api/v1", tags=["聊天"])
app.include_router(admin.router, prefix="/api/v1/admin", tags=["管理"])
app.include_router(knowledge.router, prefix="/api/v1/knowledge", tags=["知识库"])


@app.get("/health")
async def health():
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("src.main:app", host="0.0.0.0", port=8000, reload=True)
