"""Observer pattern event system for store product lifecycle events."""
from collections import defaultdict
from dataclasses import dataclass
from typing import Callable, Any
from enum import Enum


class EventType(Enum):
    """Event types for the store."""
    PRODUCT_ADDED = "product_added"
    PRODUCT_REMOVED = "product_removed"


@dataclass(frozen=True)
class Event:
    """Event class to store event information."""
    event_type: EventType
    data: dict[str, Any]


class EventManager:
    """
    Event manager implementing the Observer pattern.
    Manages event subscription and notification.
    """

    def __init__(self) -> None:
        self._listeners: defaultdict[EventType, list[Callable[[Event], None]]] = defaultdict(list)

    def subscribe(self, event_type: EventType, listener: Callable[[Event], None]) -> None:
        """Register a listener for a specific event type."""
        self._listeners[event_type].append(listener)

    def unsubscribe(self, event_type: EventType, listener: Callable[[Event], None]) -> None:
        """Unregister a listener for a specific event type."""
        if listener in self._listeners[event_type]:
            self._listeners[event_type].remove(listener)

    def notify(self, event: Event) -> None:
        """Notify all listeners subscribed to the event type."""
        for listener in self._listeners[event.event_type]:
            listener(event)

    def clear_listeners(self, event_type: EventType | None = None) -> None:
        """Clear listeners for a specific event type or all events."""
        if event_type is None:
            self._listeners.clear()
        else:
            self._listeners[event_type].clear()


# Global event manager instance
event_manager = EventManager()