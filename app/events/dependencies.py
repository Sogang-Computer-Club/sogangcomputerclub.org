"""
Event publisher dependency injection.
"""

from fastapi import Request
from .publisher import AbstractEventPublisher, NullEventPublisher


async def get_event_publisher(request: Request) -> AbstractEventPublisher:
    """
    Dependency that provides the event publisher.

    Returns the event publisher from app.state if available,
    otherwise returns a NullEventPublisher (for graceful degradation).
    """
    publisher = getattr(request.app.state, "event_publisher", None)
    if publisher is not None:
        return publisher
    return NullEventPublisher()
