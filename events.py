"""Observer pattern event system for store product lifecycle events."""
from dataclasses import dataclass
from typing import Callable, Any
from enum import Enum


class EventType(Enum):
    """Event types for the store."""
    PRODUCT_ADDED = "product_added"
    PRODUCT_REMOVED = "product_removed"


@dataclass
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
        self._listeners: dict[EventType, list[Callable[[Event], None]]] = {
            EventType.PRODUCT_ADDED: [],
            EventType.PRODUCT_REMOVED: [],
        }

    def subscribe(self, event_type: EventType, listener: Callable[[Event], None]) -> None:
        """Register a listener for a specific event type."""
        if event_type not in self._listeners:
            self._listeners[event_type] = []
        self._listeners[event_type].append(listener)

    def unsubscribe(self, event_type: EventType, listener: Callable[[Event], None]) -> None:
        """Unregister a listener for a specific event type."""
        if event_type in self._listeners and listener in self._listeners[event_type]:
            self._listeners[event_type].remove(listener)

    def notify(self, event: Event) -> None:
        """Notify all listeners subscribed to the event type."""
        if event.event_type in self._listeners:
            for listener in self._listeners[event.event_type]:
                listener(event)

    def clear_listeners(self, event_type: EventType | None = None) -> None:
        """Clear listeners for a specific event type or all events."""
        if event_type is None:
            for et in self._listeners:
                self._listeners[et] = []
        elif event_type in self._listeners:
            self._listeners[event_type] = []


# Global event manager instance
event_manager = EventManager()