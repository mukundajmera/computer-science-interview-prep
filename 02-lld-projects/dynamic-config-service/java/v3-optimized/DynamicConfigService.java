import java.util.Map;
import java.util.concurrent.atomic.AtomicReference;

class ConfigSnapshot {
    private final int version;
    private final Map<String, FeatureFlag> flags;

    public ConfigSnapshot(int version, Map<String, FeatureFlag> flags) {
        this.version = version;
        this.flags = Map.copyOf(flags);
    }

    public int getVersion() {
        return version;
    }

    public Map<String, FeatureFlag> getFlags() {
        return flags;
    }
}

public class DynamicConfigService {
    private final AtomicReference<ConfigSnapshot> currentSnapshot;
    private final Map<Integer, ConfigSnapshot> history;

    public DynamicConfigService(ConfigSnapshot initialSnapshot) {
        this.currentSnapshot = new AtomicReference<>(initialSnapshot);
        this.history = new java.util.concurrent.ConcurrentHashMap<>();
        this.history.put(initialSnapshot.getVersion(), initialSnapshot);
    }

    public boolean applySnapshot(ConfigSnapshot newSnapshot) {
        while (true) {
            ConfigSnapshot current = currentSnapshot.get();
            // Stale update: reject if new version is not greater than current version
            if (newSnapshot.getVersion() <= current.getVersion()) {
                return false;
            }
            if (currentSnapshot.compareAndSet(current, newSnapshot)) {
                history.put(newSnapshot.getVersion(), newSnapshot);
                return true;
            }
        }
    }

    public boolean rollback(int targetVersion) {
        ConfigSnapshot targetSnapshot = history.get(targetVersion);
        if (targetSnapshot == null) {
            return false;
        }

        while (true) {
            ConfigSnapshot current = currentSnapshot.get();
            if (currentSnapshot.compareAndSet(current, targetSnapshot)) {
                return true;
            }
        }
    }

    public Variant evaluate(String flagKey, UserContext context, Variant fallback) {
        ConfigSnapshot snapshot = currentSnapshot.get();
        FeatureFlag flag = snapshot.getFlags().get(flagKey);
        if (flag != null) {
            return flag.evaluate(context);
        }
        return fallback;
    }
    
    public ConfigSnapshot getCurrentSnapshot() {
        return currentSnapshot.get();
    }
}
