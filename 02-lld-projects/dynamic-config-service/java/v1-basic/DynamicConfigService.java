import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.atomic.AtomicReference;
import java.security.MessageDigest;
import java.math.BigInteger;

public class DynamicConfigService {
    private final AtomicReference<ConfigSnapshot> currentSnapshot;
    private final Map<Integer, ConfigSnapshot> history = new ConcurrentHashMap<>();

    public DynamicConfigService(ConfigSnapshot initialSnapshot) {
        this.currentSnapshot = new AtomicReference<>(initialSnapshot);
        this.history.put(initialSnapshot.getVersion(), initialSnapshot);
    }

    public boolean applySnapshot(ConfigSnapshot newSnapshot) {
        while (true) {
            ConfigSnapshot current = currentSnapshot.get();
            if (newSnapshot.getVersion() <= current.getVersion()) return false;
            if (currentSnapshot.compareAndSet(current, newSnapshot)) {
                history.put(newSnapshot.getVersion(), newSnapshot);
                return true;
            }
        }
    }

    public boolean rollback(int targetVersion) {
        ConfigSnapshot targetSnapshot = history.get(targetVersion);
        if (targetSnapshot == null) return false;
        while (true) {
            ConfigSnapshot current = currentSnapshot.get();
            if (currentSnapshot.compareAndSet(current, targetSnapshot)) return true;
        }
    }

    public Variant evaluate(String flagKey, UserContext context, Variant fallback) {
        ConfigSnapshot snapshot = currentSnapshot.get();
        FeatureFlag flag = snapshot.getFlags().get(flagKey);
        if (flag == null) return fallback;

        String tenant = context.getAttribute("tenant");
        if (tenant != null && flag.getTenantOverrides() != null && flag.getTenantOverrides().containsKey(tenant)) {
            return flag.getTenantOverrides().get(tenant);
        }

        if (flag.getRolloutPercentage() < 0 || flag.getRolloutPercentage() > 100) return fallback;

        if (flag.getRolloutPercentage() > 0) {
            try {
                String hashInput = context.getUserId() + ":" + flagKey;
                MessageDigest md = MessageDigest.getInstance("MD5");
                byte[] digest = md.digest(hashInput.getBytes("UTF-8"));
                BigInteger bigInt = new BigInteger(1, digest);
                int hashVal = bigInt.mod(BigInteger.valueOf(100)).intValue();
                if (hashVal < flag.getRolloutPercentage()) return flag.getVariant();
            } catch (Exception e) { return fallback; }
        }
        return fallback;
    }
}
