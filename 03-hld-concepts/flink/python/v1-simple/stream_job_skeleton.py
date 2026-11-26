"""Minimal stream processing skeleton for interview reasoning."""

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Generic, Optional, Protocol, TypeVar


InputT = TypeVar("InputT")
OutputT = TypeVar("OutputT")


class Source(Protocol[InputT]):
    def read_next(self) -> Optional[InputT]:
        ...


class Operator(Protocol[InputT, OutputT]):
    def process(self, input_record: InputT, event_time: datetime) -> OutputT:
        ...


class Sink(Protocol[OutputT]):
    def write(self, record: OutputT) -> None:
        ...


@dataclass(frozen=True)
class JobConfig:
    job_name: str
    checkpoint_interval_ms: int
    allowed_lateness_ms: int


class StreamJobSkeleton(Generic[InputT, OutputT]):
    """Runs a tiny source->operator->sink chain."""

    def run(self, source: Source[InputT], operator: Operator[InputT, OutputT], sink: Sink[OutputT]) -> None:
        next_record = source.read_next()
        if next_record is None:
            return
        output = operator.process(next_record, datetime.now(timezone.utc))
        sink.write(output)
