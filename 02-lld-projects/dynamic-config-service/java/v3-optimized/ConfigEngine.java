import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;

interface ConfigListener {
    void onFlagUpdated(FeatureFlag flag);
}

public class ConfigEngine {
    private final Map<String, FeatureFlag> flags = new ConcurrentHashMap<>();
    private final Map<String, List<ConfigListener>> listeners = new ConcurrentHashMap<>();

    public void updateFlag(FeatureFlag flag) {
        flags.put(flag.getKey(), flag);
        notifyListeners(flag);
    }

    public Variant evaluate(String flagKey, UserContext context) {
        FeatureFlag flag = flags.get(flagKey);
        if (flag != null) {
            return flag.evaluate(context);
        }
        return new Variant(null);
    }

    public void registerListener(String flagKey, ConfigListener listener) {
        listeners.computeIfAbsent(flagKey, k -> new ArrayList<>()).add(listener);
    }

    private void notifyListeners(FeatureFlag flag) {
        List<ConfigListener> flagListeners = listeners.get(flag.getKey());
        if (flagListeners != null) {
            for (ConfigListener listener : flagListeners) {
                // In production, execute asynchronously
                listener.onFlagUpdated(flag);
            }
        }
    }
}
