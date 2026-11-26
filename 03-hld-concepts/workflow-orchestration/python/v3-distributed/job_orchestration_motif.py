from typing import List


class JobOrchestrationMotif:
    def __init__(self) -> None:
        self.steps: List[str] = []

    def add_step(self, step_name: str) -> None:
        self.steps.append(step_name)
