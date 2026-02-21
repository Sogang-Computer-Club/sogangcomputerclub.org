"""
Event publisher dependency injection.
"""

from fastapi import Request
from .publisher import AbstractEventPublisher, NullEventPublisher


async def get_event_publisher(request: Request) -> AbstractEventPublisher:
    """
    Dependency that provides the event publisher.

    Returns the Kafka publisher from app.state if available,
    otherwise returns a NullEventPublisher (for graceful degradation).
    """
    kafka = getattr(request.app.state, "kafka", None)
    if kafka is not None:
        return kafka
    return NullEventPublisher()
