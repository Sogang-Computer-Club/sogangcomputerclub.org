"""No-op 이벤트 발행 모듈."""

import logging

logger = logging.getLogger(__name__)


class NullEventPublisher:
    """이벤트를 로깅만 하고 실제 발행하지 않는 No-op publisher."""

    async def publish(self, topic: str, message: dict) -> None:
        """Log the event but don't actually publish."""
        logger.debug(f"Event: {topic} - {message}")

    async def start(self) -> None:
        """No-op."""
        pass

    async def stop(self) -> None:
        """No-op."""
        pass
