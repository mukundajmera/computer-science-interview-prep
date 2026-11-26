import hashlib
from enum import Enum
from typing import List, Dict, Any, Optional

class Operator(Enum):
    EQUALS = 1

class UserContext:
    def __init__(self, user_id: str):
        self.user_id = user_id
        self.attributes: Dict[str, str] = {}

    def set_attribute(self, key: str, value: str):
        self.attributes[key] = value

    def get_attribute(self, key: str) -> Optional[str]:
        return self.attributes.get(key)

class Variant:
    def __init__(self, value: Any):
        self.value = value

class RolloutBucket:
    def __init__(self, percentage: int, variant: Variant):
        self.percentage = percentage
        self.variant = variant

class Rollout:
    def __init__(self, buckets: List[RolloutBucket]):
        self.buckets = buckets

    def get_variant(self, user_id: str, flag_key: str) -> Variant:
        hash_val = self._get_deterministic_hash(user_id, flag_key)
        bucket = (hash_val & 0x7FFFFFFF) % 100

        cumulative = 0
        for rb in self.buckets:
            cumulative += rb.percentage
            if bucket < cumulative:
                return rb.variant
        return Variant(None)

    def _get_deterministic_hash(self, user_id: str, flag_key: str) -> int:
        s = f"{user_id}:{flag_key}"
        h = hashlib.md5(s.encode('utf-8')).digest()
        hash_val = 0
        for i in range(4):
            hash_val = (hash_val << 8) | h[i]
        # Make it behave like a 32-bit signed integer
        if hash_val >= 2**31:
            hash_val -= 2**32
        return hash_val

class Rule:
    def __init__(self, attribute: str, operator: Operator, value: str, result: Variant = None, rollout: Rollout = None):
        self.attribute = attribute
        self.operator = operator
        self.value = value
        self.result = result
        self.rollout = rollout

    def matches(self, context: UserContext) -> bool:
        ctx_value = context.get_attribute(self.attribute)
        if ctx_value is None:
            return False
        
        if self.operator == Operator.EQUALS:
            return self.value == ctx_value
        return False

    def get_result(self, context: UserContext, flag_key: str) -> Variant:
        if self.rollout:
            return self.rollout.get_variant(context.user_id, flag_key)
        return self.result

class FeatureFlag:
    def __init__(self, key: str, default_variant: Variant, rules: List[Rule] = None):
        self.key = key
        self.default_variant = default_variant
        self.rules = rules if rules is not None else []

    def evaluate(self, context: UserContext) -> Variant:
        for rule in self.rules:
            if rule.matches(context):
                return rule.get_result(context, self.key)
        return self.default_variant
