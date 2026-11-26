from typing import Dict, List, Callable
from entities import FeatureFlag, UserContext, Variant
import threading

class ConfigEngine:
    def __init__(self):
        self.flags: Dict[str, FeatureFlag] = {}
        self.listeners: Dict[str, List[Callable[[FeatureFlag], None]]] = {}
        self.lock = threading.RLock()

    def update_flag(self, flag: FeatureFlag):
        with self.lock:
            self.flags[flag.key] = flag
        self._notify_listeners(flag)

    def evaluate(self, flag_key: str, context: UserContext) -> Variant:
        # In Python, dictionary get is atomic, so we don't strictly need a lock for reads,
        # but acquiring it makes it explicit
        with self.lock:
            flag = self.flags.get(flag_key)
        if flag:
            return flag.evaluate(context)
        return Variant(None)

    def register_listener(self, flag_key: str, listener: Callable[[FeatureFlag], None]):
        with self.lock:
            if flag_key not in self.listeners:
                self.listeners[flag_key] = []
            self.listeners[flag_key].append(listener)

    def _notify_listeners(self, flag: FeatureFlag):
        with self.lock:
            flag_listeners = self.listeners.get(flag.key, [])
        for listener in flag_listeners:
            listener(flag)
