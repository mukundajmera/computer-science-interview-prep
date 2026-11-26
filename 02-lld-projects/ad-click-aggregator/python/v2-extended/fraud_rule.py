"""FraudRule for ad-click-aggregator (v2-extended)."""

class FraudRule:
    def __init__(self) -> None:
        self.blacklisted_users = set(["fraud_user"])

    def is_fraud(self, user_id: str) -> bool:
        return user_id in self.blacklisted_users
