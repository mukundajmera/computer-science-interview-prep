"""Minimal read/write routing policy for primary + replica setups."""

from dataclasses import dataclass
from enum import Enum


class OperationType(str, Enum):
    READ = "read"
    WRITE = "write"


class Route(str, Enum):
    PRIMARY = "primary"
    REPLICA = "replica"


@dataclass(frozen=True)
class QueryContext:
    operation_type: OperationType
    requires_read_after_write: bool
    max_replica_lag_ms: int


class PostgresReadWritePlanner:
    """Decides whether a query should hit primary or replica."""

    def decide_route(self, context: QueryContext, observed_replica_lag_ms: int) -> Route:
        if context.operation_type == OperationType.WRITE:
            return Route.PRIMARY
        if context.requires_read_after_write:
            return Route.PRIMARY
        if observed_replica_lag_ms > context.max_replica_lag_ms:
            return Route.PRIMARY
        return Route.REPLICA
