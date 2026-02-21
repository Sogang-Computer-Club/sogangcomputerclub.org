"""
SQS event publisher (선택적).

사용하려면 pyproject.toml에 boto3, aioboto3 추가 필요:
    "boto3>=1.34.0",
    "aioboto3>=13.0.0",
"""

from .publisher import AbstractEventPublisher
from ..core.config import get_settings
import json
import logging
import asyncio

import aioboto3

logger = logging.getLogger(__name__)
settings = get_settings()


class SQSEventPublisher(AbstractEventPublisher):
    """
    AWS SQS event publisher.

    Uses aioboto3 for async SQS operations.
    Messages include the topic as a message attribute for routing.
    Reuses a single SQS client for efficiency.
    """

    def __init__(self):
        self._session = None
        self._client = None
        self._client_context = None
        self._queue_url = settings.sqs_queue_url

    async def start(self) -> None:
        """SQS 클라이언트 초기화."""
        if not self._queue_url:
            logger.warning("SQS_QUEUE_URL not set, SQS publisher disabled")
            return

        try:
            self._session = aioboto3.Session()
            self._client_context = self._session.client(
                "sqs", region_name=settings.aws_region
            )
            self._client = await self._client_context.__aenter__()
            logger.info(f"SQS publisher initialized for queue: {self._queue_url}")
        except Exception as e:
            logger.warning(f"Failed to initialize SQS publisher: {e}")

    async def stop(self) -> None:
        """Cleanup SQS resources."""
        if self._client_context:
            try:
                await self._client_context.__aexit__(None, None, None)
            except Exception as e:
                logger.warning(f"Error closing SQS client: {e}")
        self._client = None
        self._client_context = None
        self._session = None
        logger.info("SQS publisher stopped")

    async def publish(self, topic: str, message: dict, max_retries: int = 3) -> None:
        """SQS에 메시지 발행 (재시도 로직 포함)."""
        if not self._client or not self._queue_url:
            return

        last_error = None

        for attempt in range(max_retries):
            try:
                await self._client.send_message(
                    QueueUrl=self._queue_url,
                    MessageBody=json.dumps(message),
                    MessageAttributes={
                        "topic": {"DataType": "String", "StringValue": topic}
                    },
                )
                logger.debug(f"Published message to SQS topic={topic}")
                return
            except Exception as e:
                last_error = e
                if attempt < max_retries - 1:
                    wait_time = 0.5 * (2**attempt)
                    logger.warning(
                        f"SQS publish failed (attempt {attempt + 1}/{max_retries}), retrying in {wait_time}s: {e}"
                    )
                    await asyncio.sleep(wait_time)

        logger.error(
            f"Failed to publish to SQS after {max_retries} attempts: {last_error}"
        )

    @property
    def is_connected(self) -> bool:
        """Check if SQS publisher is ready."""
        return self._client is not None and self._queue_url is not None
