"""
이벤트 발행 (No-op).

동아리 프로젝트 규모에서 Kafka/SQS 이벤트 시스템은 불필요하므로
이벤트를 로깅만 하고 실제 발행하지 않는 NullEventPublisher만 제공.
"""

import logging

logger = logging.getLogger(__name__)


class NullEventPublisher:
    """
    No-op event publisher (기본값).

    이벤트를 로깅만 하고 실제 발행하지 않음.
    """

    async def publish(self, topic: str, message: dict) -> None:
        """Log the event but don't actually publish."""
        logger.debug(f"Event: {topic} - {message}")

    async def start(self) -> None:
        """No-op."""
        pass

    async def stop(self) -> None:
        """No-op."""
        pass
