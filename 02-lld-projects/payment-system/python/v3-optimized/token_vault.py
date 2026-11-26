"""TokenVault for payment-system (v3-optimized)."""


class TokenVault:
    def __init__(self) -> None:
        self.id = "TokenVault"

    def describe(self) -> str:
        return f"TokenVault:{self.id}"
