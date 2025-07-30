# main.py
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import StreamingResponse
from auth import get_current_user
from database import get_db
from kafka_consumer import kafka_stream

# from redis_utils import subscribe
# import asyncio
from sqlalchemy.orm import Session


router = APIRouter(prefix="/sse")


@router.get("/events")
async def sse_endpoint(request: Request, db: Session = Depends(get_db)):
    token = request.query_params.get("token")
    if not token:
        raise HTTPException(status_code=401, detail="Token missing")

    user = get_current_user(token=token, db=db)

    topic = request.query_params.get("channel", "create_blog")

    return StreamingResponse(
        kafka_stream(request, topic), media_type="text/event-stream"
    )
