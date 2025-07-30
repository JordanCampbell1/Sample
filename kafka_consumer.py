# kafka_consumer.py
from aiokafka import AIOKafkaConsumer
import asyncio

# KAFKA_BOOTSTRAP_SERVERS = "localhost:9092"
KAFKA_BOOTSTRAP_SERVERS = "localhost:9092"
KAFKA_GROUP_ID = "sse-group"


async def kafka_stream(request, topic: str):
    loop = asyncio.get_event_loop()
    consumer = AIOKafkaConsumer(
        topic,
        loop=loop,
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        group_id=KAFKA_GROUP_ID,
        auto_offset_reset="latest",
    )
    await consumer.start()
    try:
        async for message in consumer:
            if await request.is_disconnected():
                break
            yield f"data: {message.value.decode()}\n\n"
            await asyncio.sleep(0.05)
    finally:
        await consumer.stop()
