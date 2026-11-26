"""Simple SQL vs NoSQL selector based on workload requirements."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Workload:
    needs_strong_transactions: bool
    needs_flexible_schema: bool
    needs_join_heavy_queries: bool
    needs_massive_horizontal_scale: bool


def choose_store(workload: Workload) -> str:
    if workload.needs_strong_transactions or workload.needs_join_heavy_queries:
        return "SQL"
    if workload.needs_massive_horizontal_scale or workload.needs_flexible_schema:
        return "NoSQL"
    return "SQL"


if __name__ == "__main__":
    print(choose_store(Workload(True, False, True, False)))
    print(choose_store(Workload(False, True, False, True)))
