# main.py
from fastapi import APIRouter, FastAPI, Request
from fastapi.responses import StreamingResponse
from redis_utils import subscribe
import asyncio

router = APIRouter(prefix="/sse")

@router.get("/events")
async def sse_endpoint(request: Request):
    async def event_stream():
        pubsub = await subscribe("updates")
        try:
            while True:
                message = await pubsub.get_message(ignore_subscribe_messages=True, timeout=1.0)
                if message:
                    yield f"data: {message['data']}\n\n"
                await asyncio.sleep(0.01)
                if await request.is_disconnected():
                    break
        finally:
            await pubsub.unsubscribe("updates")
            await pubsub.close()

    return StreamingResponse(event_stream(), media_type="text/event-stream")
