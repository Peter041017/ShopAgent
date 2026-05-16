from fastapi import APIRouter

router = APIRouter()


@router.post("/reindex")
async def trigger_reindex():
    """占位：生产可触发异步重建索引任务"""
    return {"accepted": True, "message": "请运行 scripts/build_index.py 或调用内部任务队列"}
