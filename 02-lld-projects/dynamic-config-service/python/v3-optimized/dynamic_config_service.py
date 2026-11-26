import threading
from typing import Dict
from entities import FeatureFlag, UserContext, Variant

class ConfigSnapshot:
    def __init__(self, version: int, flags: Dict[str, FeatureFlag]):
        self.version = version
        self.flags = dict(flags)

class DynamicConfigService:
    def __init__(self, initial_snapshot: ConfigSnapshot):
        self.current_snapshot = initial_snapshot
        self.history: Dict[int, ConfigSnapshot] = {initial_snapshot.version: initial_snapshot}
        self.lock = threading.RLock()

    def apply_snapshot(self, new_snapshot: ConfigSnapshot) -> bool:
        with self.lock:
            if new_snapshot.version <= self.current_snapshot.version:
                return False
            self.current_snapshot = new_snapshot
            self.history[new_snapshot.version] = new_snapshot
            return True

    def rollback(self, target_version: int) -> bool:
        with self.lock:
            if target_version not in self.history:
                return False
            self.current_snapshot = self.history[target_version]
            return True

    def evaluate(self, flag_key: str, context: UserContext, fallback: Variant) -> Variant:
        with self.lock:
            snapshot = self.current_snapshot
        
        flag = snapshot.flags.get(flag_key)
        if flag is not None:
            return flag.evaluate(context)
        return fallback

    def get_current_snapshot(self) -> ConfigSnapshot:
        with self.lock:
            return self.current_snapshot
