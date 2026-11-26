"""Minimal LeetCode-style judge orchestration skeleton.

This module intentionally focuses on interfaces and flow boundaries.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, List, Optional, Protocol
from uuid import UUID, uuid4


class SubmissionStatus(str, Enum):
    QUEUED = "QUEUED"
    RUNNING = "RUNNING"
    ACCEPTED = "ACCEPTED"
    WRONG_ANSWER = "WRONG_ANSWER"
    TIME_LIMIT_EXCEEDED = "TIME_LIMIT_EXCEEDED"
    MEMORY_LIMIT_EXCEEDED = "MEMORY_LIMIT_EXCEEDED"
    RUNTIME_ERROR = "RUNTIME_ERROR"
    COMPILE_ERROR = "COMPILE_ERROR"
    SYSTEM_ERROR = "SYSTEM_ERROR"

    @property
    def is_terminal(self) -> bool:
        return self not in {SubmissionStatus.QUEUED, SubmissionStatus.RUNNING}


@dataclass(frozen=True)
class SubmissionRequest:
    user_id: UUID
    language: str
    source_code: str
    test_bundle_ref: str
    runtime_limit_ms: int
    memory_limit_mb: int
    contest_id: Optional[UUID] = None


@dataclass
class Submission:
    submission_id: UUID
    user_id: UUID
    status: SubmissionStatus
    contest_id: Optional[UUID] = None
    sandbox_job_id: Optional[str] = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass(frozen=True)
class SandboxJobHandle:
    job_id: str


@dataclass(frozen=True)
class SandboxExecutionResult:
    verdict: Optional[str]
    score: float = 0.0
    terminal: bool = False


@dataclass(frozen=True)
class LeaderboardEntry:
    user_id: UUID
    score: float
    rank: int


@dataclass(frozen=True)
class LeaderboardSnapshot:
    contest_id: UUID
    generated_at: datetime
    entries: List[LeaderboardEntry]


class ExecutionSandbox(Protocol):
    def submit(
        self,
        submission_id: UUID,
        language: str,
        source_code: str,
        test_bundle_ref: str,
        runtime_limit_ms: int,
        memory_limit_mb: int,
    ) -> SandboxJobHandle:
        ...

    def cancel(self, sandbox_job_id: str) -> bool:
        ...

    def get_status(self, sandbox_job_id: str) -> Optional[SandboxExecutionResult]:
        ...


class LeaderboardProjection(Protocol):
    def record_result(self, contest_id: UUID, user_id: UUID, score: float) -> None:
        ...

    def top_k(self, contest_id: UUID, k: int) -> List[LeaderboardEntry]:
        ...

    def snapshot(self, contest_id: UUID) -> Optional[LeaderboardSnapshot]:
        ...


class SubmissionRepository(Protocol):
    def save(self, submission: Submission) -> None:
        ...

    def get(self, submission_id: UUID) -> Optional[Submission]:
        ...

    def bind_handle(self, submission_id: UUID, sandbox_job_id: str) -> None:
        ...

    def mark_completed(
        self,
        submission_id: UUID,
        status: SubmissionStatus,
        result: SandboxExecutionResult,
    ) -> None:
        ...


class JudgeOrchestrator:
    def __init__(
        self,
        execution_sandbox: ExecutionSandbox,
        leaderboard_projection: LeaderboardProjection,
        submission_repository: SubmissionRepository,
    ) -> None:
        self._execution_sandbox = execution_sandbox
        self._leaderboard_projection = leaderboard_projection
        self._submission_repository = submission_repository

    def submit_for_judging(self, request: SubmissionRequest) -> Submission:
        submission = Submission(
            submission_id=uuid4(),
            user_id=request.user_id,
            contest_id=request.contest_id,
            status=SubmissionStatus.QUEUED,
        )
        self._submission_repository.save(submission)

        handle = self._execution_sandbox.submit(
            submission_id=submission.submission_id,
            language=request.language,
            source_code=request.source_code,
            test_bundle_ref=request.test_bundle_ref,
            runtime_limit_ms=request.runtime_limit_ms,
            memory_limit_mb=request.memory_limit_mb,
        )
        self._submission_repository.bind_handle(submission.submission_id, handle.job_id)
        return submission

    def poll_submission_status(self, submission_id: UUID) -> SubmissionStatus:
        submission = self._submission_repository.get(submission_id)
        if submission is None:
            raise ValueError("Unknown submission")

        if submission.status.is_terminal:
            return submission.status

        if not submission.sandbox_job_id:
            return SubmissionStatus.QUEUED

        latest = self._execution_sandbox.get_status(submission.sandbox_job_id)
        if latest is None or not latest.terminal:
            return SubmissionStatus.RUNNING

        terminal = _to_submission_status(latest.verdict)
        self._submission_repository.mark_completed(submission_id, terminal, latest)

        if terminal == SubmissionStatus.ACCEPTED and submission.contest_id is not None:
            self._leaderboard_projection.record_result(
                contest_id=submission.contest_id,
                user_id=submission.user_id,
                score=latest.score,
            )

        return terminal

    def contest_top_k(self, contest_id: UUID, k: int) -> List[LeaderboardEntry]:
        return self._leaderboard_projection.top_k(contest_id, k)

    def contest_snapshot(self, contest_id: UUID) -> Optional[LeaderboardSnapshot]:
        return self._leaderboard_projection.snapshot(contest_id)


class InMemoryLeaderboardProjection:
    def __init__(self) -> None:
        self._scores: Dict[UUID, Dict[UUID, float]] = {}

    def record_result(self, contest_id: UUID, user_id: UUID, score: float) -> None:
        contest_scores = self._scores.setdefault(contest_id, {})
        current = contest_scores.get(user_id, 0.0)
        contest_scores[user_id] = max(current, score)

    def top_k(self, contest_id: UUID, k: int) -> List[LeaderboardEntry]:
        contest_scores = self._scores.get(contest_id, {})
        sorted_items = sorted(contest_scores.items(), key=lambda item: item[1], reverse=True)
        entries: List[LeaderboardEntry] = []
        for rank, (user_id, score) in enumerate(sorted_items[:k], start=1):
            entries.append(LeaderboardEntry(user_id=user_id, score=score, rank=rank))
        return entries

    def snapshot(self, contest_id: UUID) -> Optional[LeaderboardSnapshot]:
        if contest_id not in self._scores:
            return None
        return LeaderboardSnapshot(
            contest_id=contest_id,
            generated_at=datetime.now(timezone.utc),
            entries=self.top_k(contest_id, 100),
        )


def _to_submission_status(verdict: Optional[str]) -> SubmissionStatus:
    mapping = {
        "AC": SubmissionStatus.ACCEPTED,
        "WA": SubmissionStatus.WRONG_ANSWER,
        "TLE": SubmissionStatus.TIME_LIMIT_EXCEEDED,
        "MLE": SubmissionStatus.MEMORY_LIMIT_EXCEEDED,
        "RE": SubmissionStatus.RUNTIME_ERROR,
        "CE": SubmissionStatus.COMPILE_ERROR,
    }
    return mapping.get(verdict, SubmissionStatus.SYSTEM_ERROR)
