"""RiskRule for payment-system (v2-extended)."""


class RiskRule:
    def __init__(self) -> None:
        self.id = "RiskRule"

    def describe(self) -> str:
        return f"RiskRule:{self.id}"
# Substantive change for review
