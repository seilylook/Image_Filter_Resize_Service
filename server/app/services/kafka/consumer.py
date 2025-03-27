from confluent_kafka import Consumer, KafkaError
from app.core.config import settings
from app.core.logging import get_logger
import json
from typing import Dict, Any, Callable, List, Optional

logger = get_logger(__name__)


class KafkaConsumerService:
    """Kafka 컨슈머 서비스"""

    def __init__(
        self,
        topics: List[str],
        group_id: str,
        auto_offset_reset: str = "earliest",
    ):
        self.config = {
            "bootstrap.servers": settings.KAFKA_BOOTSTRAP_SERVERS,
            "group.id": group_id,
            "auto.offset.reset": auto_offset_reset,
            "enable.auto.commit": False,
        }
        self.topics = topics
        self.consumer = Consumer(self.config)
        self.consumer.subscribe(topics)
        logger.info(f"Kafka consumer initialized for topics: {topics}")

    def consume_messages(
        self,
        process_message: Callable[[str, Optional[str], Dict[str, Any]], bool],
        timeout: float = 1.0,
        max_messages: int = 100,
    ):
        """메시지 소비 및 처리"""
        messages_processed = 0

        try:
            while messages_processed < max_messages:
                msg = self.consumer.poll(timeout)

                if msg is None:
                    continue

                if msg.error():
                    if msg.error().code() == KafkaError._PARTITION_EOF:
                        logger.debug(
                            f"Reached end of partition {msg.topic()}/{msg.partition()}"
                        )
                    else:
                        logger.error(f"Consumer error: {msg.error()}")
                    continue

                try:
                    topic = msg.topic()
                    key = msg.key().decode("utf-8") if msg.key() else None
                    value = json.loads(msg.value().decode("utf-8"))

                    # 메시지 처리 콜백 함수 호출
                    processed = process_message(topic, key, value)

                    # 처리 완료된 메시지만 오프셋 커밋
                    if processed:
                        self.consumer.commit(msg)
                        messages_processed += 1

                except json.JSONDecodeError:
                    logger.error(f"Failed to parse message: {msg.value()}")
                except Exception as e:
                    logger.error(f"Error processing message: {str(e)}")

        except Exception as e:
            logger.error(f"Consumer Error: {str(e)}")
        finally:
            return messages_processed

    def close(self):
        """컨슈머 연결 종료"""
        self.consumer.close()
        logger.info("Kafka consumer closed")


def get_kafka_consumer(topics: List[str], group_id: str):
    """종속성 주입용 함수"""
    consumer = KafkaConsumerService(topics=topics, group_id=group_id)
    try:
        yield consumer
    finally:
        consumer.close()
