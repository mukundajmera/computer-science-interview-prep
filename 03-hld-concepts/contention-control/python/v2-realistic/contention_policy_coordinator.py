"""v2-realistic: policy coordinator for contention control."""

from collections import defaultdict, deque
from enum import Enum
from typing import Callable, Deque, Dict, TypeVar


T = TypeVar("T")


class ContentionPolicy(str, Enum):
    OPTIMISTIC = "optimistic"
    PESSIMISTIC = "pessimistic"
    SERIAL_QUEUE = "serial_queue"
    DISTRIBUTED_LOCK = "distributed_lock"


class ContentionPolicyCoordinator:
    def __init__(self) -> None:
        self._policy_by_resource: Dict[str, ContentionPolicy] = {}
        self._queue_by_resource: Dict[str, Deque[Callable[[], object]]] = defaultdict(deque)

    def set_policy(self, resource_key: str, policy: ContentionPolicy) -> None:
        self._policy_by_resource[resource_key] = policy

    def execute(self, resource_key: str, action: Callable[[], T]) -> T:
        policy = self._policy_by_resource.get(resource_key, ContentionPolicy.OPTIMISTIC)
        if policy == ContentionPolicy.SERIAL_QUEUE:
            queue = self._queue_by_resource[resource_key]
            queue.append(action)
            fn = queue.popleft()
            return fn()  # type: ignore[return-value]
        return action()
