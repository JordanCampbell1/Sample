# test.py
import asyncio
import logging
from kafka_producer import publish_event, close_producer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def main():
    try:
        # Example usage of the publish_event function
        await publish_event("test_topic", "Hello, Kafka!")
        logger.info("Message published successfully!")

        # You can add more messages here for testing
        await publish_event("test_topic", "Another test message")

    except Exception as e:
        logger.error(f"Error in main: {e}")
    finally:
        # Clean up the producer connection
        await close_producer()


if __name__ == "__main__":
    asyncio.run(main())
