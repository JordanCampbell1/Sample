import redis

import redis.asyncio as asnyc_redis


redis_client = redis.Redis(host="localhost", port=6379, decode_responses=True)

async_redis_client = asnyc_redis.Redis(
    host="localhost", port=6379, decode_responses=True
)


async def publish_event(channel: str, message: str):
    await async_redis_client.publish(channel, message)


async def subscribe(channel: str):
    pubsub = async_redis_client.pubsub()
    await pubsub.subscribe(channel)
    return pubsub
