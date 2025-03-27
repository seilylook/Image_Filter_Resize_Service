from confluent_kafka import Producer
from app.core.config import settings
from app.core.logging import get_logger
import json
import time
from typing import Dict, Any, Optional, Callable

logger = get_logger(__name__)


class KafkaProducerService:
    """Kafka 프로듀서 서비스"""

    def __init__(self):
        self.config = {
            "bootstrap.servers": settings.KAFKA_BOOTSTRAP_SERVERS,
            "client.id": settings.SERVICE_NAME,
            "acks": "all",
            "retries": 3,
            "retry.backoff.ms": 100,
        }
        self.producer = Producer(self.config)
        logger.info(
            f"Kafka producer initialized with bootstrap servers: {settings.KAFKA_BOOTSTRAP_SERVERS}"
        )

    def send_message(
        self,
        topic: str,
        key: str,
        value: Dict[str, Any],
        callback: Optional[Callable] = None,
    ) -> bool:
        """kafka 토픽으로 메시지 전송"""
        try:
            value_bytes = json.dumps(value).encode("utf-8")
            key_bytes = key.encode("utf-8") if key else None

            if callback is None:
                callback = self._delivery_report

            self.producer.produce(
                topic=topic, key=key_bytes, value=value_bytes, callback=callback
            )

            self.producer.poll(0)
            logger.debug(
                f"Kafka 메시지 생성에 성공했습니다: topic {topic} with key {key}"
            )
            return True
        except Exception as e:
            logger.error(f"Kafka 메시지 생성에 실패했습니다: {str(e)}")

    def _delivery_report(self, err, msg):
        """메시지 전송 결과 콜백"""
        if err is not None:
            logger.error(f"Message delivery failed: {err}")
        else:
            topic = msg.topic()
            partition = msg.partition()
            offset = msg.offset()
            key = msg.key().decode("utf-8") if msg.key() else None
            logger.debug(
                f"Message delivered to {topic}[{partition}]@{offset} with key={key}"
            )

    def flush(self, timeout: float = 10.0):
        """대기 중인 모든 메시지 전송"""
        self.producer.flush(timeout)


def get_kafka_producer():
    """종속성 주입용 함수"""
    producer = KafkaProducerService()
    try:
        yield producer
    finally:
        producer.flush()
