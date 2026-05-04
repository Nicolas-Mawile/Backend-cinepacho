"""Event bus for domain events."""

import queue
from typing import Any, Callable, Dict, List


class EventBus:
    def __init__(self):
        self._subscribers: Dict[str, List[Callable[[Any], Any]]] = {}
        self._queue = queue.Queue()

    def subscribe(self, event_type: str, handler: Callable[[Any], Any]):
        self._subscribers.setdefault(event_type, []).append(handler)

    def publish(self, event_type: str, payload: Any):
        self._queue.put((event_type, payload))

    def dispatch(self):
        while not self._queue.empty():
            event_type, payload = self._queue.get()
            for handler in self._subscribers.get(event_type, []):
                handler(payload)
