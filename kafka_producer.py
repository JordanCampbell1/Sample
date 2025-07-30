# kafka_producer.py - Minimal version
from aiokafka import AIOKafkaProducer
from aiokafka.errors import KafkaConnectionError
import asyncio
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

KAFKA_BOOTSTRAP_SERVERS = "localhost:9092"

producer = None


async def get_producer():
    global producer
    if producer is None:
        loop = asyncio.get_event_loop()
        producer = AIOKafkaProducer(
            bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS, loop=loop
        )
        try:
            await producer.start()
            logger.info("Kafka producer started successfully")
        except KafkaConnectionError as e:
            logger.error(f"Failed to connect to Kafka: {e}")
            logger.error("Make sure Kafka is running on localhost:9092")
            producer = None
            raise
    return producer


async def publish_event(topic: str, message: str):
    try:
        p = await get_producer()
        await p.send_and_wait(topic, message.encode())
        logger.info(f"Message sent to topic {topic}: {message}")
    except Exception as e:
        logger.error(f"Error publishing message: {e}")
        raise


async def close_producer():
    """Clean up the producer connection"""
    global producer
    if producer:
        try:
            await producer.stop()
            logger.info("Kafka producer stopped")
        except Exception as e:
            logger.error(f"Error stopping producer: {e}")
        finally:
            producer = None
