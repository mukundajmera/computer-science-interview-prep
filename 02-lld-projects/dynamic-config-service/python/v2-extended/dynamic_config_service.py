import hashlib
from typing import Dict, Optional
from entities import FeatureFlag, UserContext, Variant

class ConfigSnapshot:
    def __init__(self, version: int, flags: Dict[str, FeatureFlag]):
        self.version = version
        self.flags = flags

class DynamicConfigService:
    def __init__(self, initial_snapshot: ConfigSnapshot):
        self.current_snapshot = initial_snapshot
        self.history: Dict[int, ConfigSnapshot] = {initial_snapshot.version: initial_snapshot}

    def apply_snapshot(self, new_snapshot: ConfigSnapshot) -> bool:
        if new_snapshot.version <= self.current_snapshot.version:
            return False
        self.current_snapshot = new_snapshot
        self.history[new_snapshot.version] = new_snapshot
        return True

    def rollback(self, target_version: int) -> bool:
        target_snapshot = self.history.get(target_version)
        if target_snapshot is None:
            return False
        self.current_snapshot = target_snapshot
        return True

    def evaluate(self, flag_key: str, context: UserContext, fallback: Variant) -> Variant:
        snapshot = self.current_snapshot
        flag = snapshot.flags.get(flag_key)
        if flag is None:
            return fallback

        tenant = context.get_attribute("tenant")
        if tenant is not None and flag.tenant_overrides and tenant in flag.tenant_overrides:
            return flag.tenant_overrides[tenant]
            
        rule_result = flag.evaluate_rules(context)
        if rule_result is not None:
            return rule_result

        if flag.rollout_percentage < 0 or flag.rollout_percentage > 100:
            return fallback

        if flag.rollout_percentage > 0:
            hash_input = f"{context.user_id}:{flag_key}".encode('utf-8')
            md5_hash = hashlib.md5(hash_input).hexdigest()
            hash_val = int(md5_hash, 16) % 100
            if hash_val < flag.rollout_percentage:
                return flag.default_variant
        
        return fallback
