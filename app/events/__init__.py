"""Event publishing module."""

from .publisher import (
    AbstractEventPublisher,
    NullEventPublisher,
    create_event_publisher,
)
from .dependencies import get_event_publisher

__all__ = [
    "AbstractEventPublisher",
    "NullEventPublisher",
    "create_event_publisher",
    "get_event_publisher",
]

# Kafka/SQS publishers are in separate files and imported on-demand
# to avoid import errors when dependencies are not installed.
