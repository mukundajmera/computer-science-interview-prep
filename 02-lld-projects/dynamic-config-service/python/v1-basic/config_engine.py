import hashlib

class Variant:
    def __init__(self, value):
        self.value = value

class UserContext:
    def __init__(self, user_id):
        self.user_id = user_id
        self.attributes = {}
    
    def set_attribute(self, key, value):
        self.attributes[key] = value
    
    def get_attribute(self, key):
        return self.attributes.get(key)

class FeatureFlag:
    def __init__(self, key, variant, rollout_percentage, tenant_overrides=None):
        self.key = key
        self.variant = variant
        self.rollout_percentage = rollout_percentage
        self.tenant_overrides = tenant_overrides if tenant_overrides is not None else {}

class ConfigSnapshot:
    def __init__(self, version, flags):
        self.version = version
        self.flags = flags

class DynamicConfigService:
    def __init__(self, initial_snapshot):
        self.current_snapshot = initial_snapshot
        self.history = {initial_snapshot.version: initial_snapshot}

    def apply_snapshot(self, new_snapshot):
        if new_snapshot.version <= self.current_snapshot.version:
            return False
        self.current_snapshot = new_snapshot
        self.history[new_snapshot.version] = new_snapshot
        return True

    def rollback(self, target_version):
        target_snapshot = self.history.get(target_version)
        if target_snapshot is None:
            return False
        self.current_snapshot = target_snapshot
        return True

    def evaluate(self, flag_key, context, fallback):
        snapshot = self.current_snapshot
        flag = snapshot.flags.get(flag_key)
        if flag is None:
            return fallback

        tenant = context.get_attribute("tenant")
        if tenant is not None and flag.tenant_overrides and tenant in flag.tenant_overrides:
            return flag.tenant_overrides[tenant]

        if flag.rollout_percentage < 0 or flag.rollout_percentage > 100:
            return fallback

        if flag.rollout_percentage > 0:
            hash_input = f"{context.user_id}:{flag_key}".encode('utf-8')
            md5_hash = hashlib.md5(hash_input).hexdigest()
            hash_val = int(md5_hash, 16) % 100
            if hash_val < flag.rollout_percentage:
                return flag.variant
        
        return fallback
