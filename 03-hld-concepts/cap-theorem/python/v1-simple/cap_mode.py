"""Simple CAP behavior simulator during partition events."""

from dataclasses import dataclass


@dataclass(frozen=True)
class CapDecision:
    mode: str  # CP or AP

    def __post_init__(self) -> None:
        if self.mode not in {"CP", "AP"}:
            raise ValueError("mode must be CP or AP")


class CapSystem:
    def __init__(self, decision: CapDecision):
        self._decision = decision

    def read_during_partition(self) -> str:
        if self._decision.mode == "CP":
            return "REJECTED_FOR_CONSISTENCY"
        return "STALE_OK"


if __name__ == "__main__":
    print(CapSystem(CapDecision("CP")).read_during_partition())
    print(CapSystem(CapDecision("AP")).read_during_partition())
