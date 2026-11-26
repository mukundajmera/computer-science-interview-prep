from typing import Dict, Optional
from entities import FeatureFlag, UserContext, Variant

class ConfigEngine:
    def __init__(self):
        self.flags: Dict[str, FeatureFlag] = {}

    def update_flag(self, flag: FeatureFlag):
        self.flags[flag.key] = flag

    def evaluate(self, flag_key: str, context: UserContext) -> Variant:
        flag = self.flags.get(flag_key)
        if flag:
            return flag.evaluate(context)
        return Variant(None)
