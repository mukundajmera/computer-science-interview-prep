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

class Rule:
    def __init__(self, attribute: str, operator: Operator, value: str, result: Variant):
        self.attribute = attribute
        self.operator = operator
        self.value = value
        self.result = result

    def matches(self, context: UserContext) -> bool:
        ctx_value = context.get_attribute(self.attribute)
        if ctx_value is None:
            return False
        
        if self.operator == Operator.EQUALS:
            return self.value == ctx_value
        return False

class FeatureFlag:
    def __init__(self, key: str, default_variant: Variant, rules: List[Rule] = None, rollout_percentage: int = 0, tenant_overrides: Dict[str, Variant] = None):
        self.key = key
        self.default_variant = default_variant
        self.rules = rules if rules is not None else []
        self.rollout_percentage = rollout_percentage
        self.tenant_overrides = tenant_overrides if tenant_overrides is not None else {}

    def evaluate(self, context: UserContext) -> Variant:
        rule_result = self.evaluate_rules(context)
        if rule_result is not None:
            return rule_result
        return self.default_variant
        
    def evaluate_rules(self, context: UserContext) -> Optional[Variant]:
        for rule in self.rules:
            if rule.matches(context):
                return rule.result
        return None
