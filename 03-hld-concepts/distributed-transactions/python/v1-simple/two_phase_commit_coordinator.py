import time
from typing import List, Optional

class Participant:
    def prepare(self) -> bool:
        """Vote on whether the transaction can be committed."""
        raise NotImplementedError

    def commit(self) -> bool:
        """Commit the transaction."""
        raise NotImplementedError

    def abort(self) -> bool:
        """Abort the transaction."""
        raise NotImplementedError

class TwoPhaseCommitCoordinator:
    def __init__(self, participants: List[Participant], timeout_ms: int = 1000):
        self.participants = participants
        self.timeout_ms = timeout_ms
        self.wal: List[str] = []

    def execute_transaction(self) -> bool:
        self.wal.append("TX_START")

        # Phase 1: Prepare
        prepared_participants: List[Participant] = []
        all_prepared = True

        for p in self.participants:
            try:
                # Mocking timeout with a simple try-catch block for demo purposes
                # In a real system, async with a timeout or threading would be used
                vote = p.prepare()
                if vote:
                    prepared_participants.append(p)
                    self.wal.append(f"PREPARE_OK")
                else:
                    self.wal.append(f"PREPARE_NO")
                    all_prepared = False
                    break
            except Exception:
                self.wal.append(f"PREPARE_ERR")
                all_prepared = False
                break

        # Phase 2: Commit or Abort
        if all_prepared:
            self.wal.append("COMMIT_START")
            commit_success = True
            for p in prepared_participants:
                try:
                    success = p.commit()
                    if success:
                        self.wal.append("COMMIT_OK")
                    else:
                        self.wal.append("COMMIT_ERR")
                        commit_success = False
                except Exception:
                    self.wal.append("COMMIT_ERR")
                    commit_success = False

            if commit_success:
                self.wal.append("TX_COMMITTED")
                return True
            else:
                self.wal.append("TX_INCONSISTENT") # Needs manual intervention
                return False
        else:
            self.wal.append("ABORT_START")
            for p in prepared_participants:
                try:
                    success = p.abort()
                    if success:
                        self.wal.append("ABORT_OK")
                    else:
                        self.wal.append("ABORT_ERR")
                except Exception:
                    self.wal.append("ABORT_ERR")
            self.wal.append("TX_ABORTED")
            return False

class SagaStep:
    def execute(self) -> bool:
        """Execute the forward action."""
        raise NotImplementedError

    def compensate(self) -> bool:
        """Execute the backward compensating action."""
        raise NotImplementedError

class SagaOrchestrator:
    def __init__(self, steps: List[SagaStep]):
        self.steps = steps
        self.state = "INIT"
        self.executed_steps: List[SagaStep] = []

    def execute(self) -> bool:
        self.state = "RUNNING"

        for step in self.steps:
            try:
                success = step.execute()
                if success:
                    self.executed_steps.append(step)
                else:
                    self.state = "COMPENSATING"
                    self._compensate()
                    return False
            except Exception:
                self.state = "COMPENSATING"
                self._compensate()
                return False

        self.state = "COMPLETED"
        return True

    def _compensate(self):
        for step in reversed(self.executed_steps):
            try:
                step.compensate()
            except Exception:
                # Log error and potentially queue for manual intervention
                pass
        self.state = "COMPENSATED"
