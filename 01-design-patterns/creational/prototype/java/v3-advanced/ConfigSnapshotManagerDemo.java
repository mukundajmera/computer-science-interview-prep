package prototype.v3;

import java.util.ArrayDeque;
import java.util.Collections;
import java.util.Deque;
import java.util.HashMap;
import java.util.Map;

/**
 * v3-advanced: Copy-on-Write Versioned Configuration Snapshot Manager.
 * Demonstrates prototype cloning applied to state snapshots for transactional rollback,
 * audit trails, and branching configuration environments.
 */
public class ConfigSnapshotManagerDemo {

    public static class ConfigSnapshot implements Cloneable {
        private final int version;
        private final Map<String, String> properties;
        private final Map<String, Integer> limits;

        public ConfigSnapshot(int version, Map<String, String> properties, Map<String, Integer> limits) {
            this.version = version;
            this.properties = new HashMap<>(properties);
            this.limits = new HashMap<>(limits);
        }

        public int getVersion() {
            return version;
        }

        public Map<String, String> getProperties() {
            return Collections.unmodifiableMap(properties);
        }

        public Map<String, Integer> getLimits() {
            return Collections.unmodifiableMap(limits);
        }

        public String getProperty(String key) {
            return properties.get(key);
        }

        public Integer getLimit(String key) {
            return limits.get(key);
        }

        /**
         * Clones this snapshot to yield a new editable draft incremented to target version.
         */
        public ConfigSnapshot createDraft(int nextVersion) {
            return new ConfigSnapshot(nextVersion, new HashMap<>(this.properties), new HashMap<>(this.limits));
        }

        public void setProperty(String key, String value) {
            this.properties.put(key, value);
        }

        public void setLimit(String key, int limit) {
            this.limits.put(key, limit);
        }
    }

    public static class ConfigurationManager {
        private ConfigSnapshot current;
        private final Deque<ConfigSnapshot> history = new ArrayDeque<>();

        public ConfigurationManager(Map<String, String> initialProps, Map<String, Integer> initialLimits) {
            this.current = new ConfigSnapshot(1, initialProps, initialLimits);
        }

        public ConfigSnapshot getCurrent() {
            return current;
        }

        public void commitUpdate(java.util.function.Consumer<ConfigSnapshot> updater) {
            // Push clone of current state to history stack
            history.push(current.createDraft(current.getVersion()));
            ConfigSnapshot nextDraft = current.createDraft(current.getVersion() + 1);
            updater.accept(nextDraft);
            this.current = nextDraft;
        }

        public boolean rollback() {
            if (history.isEmpty()) {
                return false;
            }
            this.current = history.pop();
            return true;
        }

        public int getHistoryDepth() {
            return history.size();
        }
    }

    public static void main(String[] args) {
        ConfigurationManager manager = new ConfigurationManager(
                Map.of("env", "prod", "db_host", "db.internal"),
                Map.of("max_connections", 100, "timeout_ms", 3000)
        );

        System.out.println("V1 host: " + manager.getCurrent().getProperty("db_host"));

        manager.commitUpdate(draft -> {
            draft.setProperty("db_host", "new-db.internal");
            draft.setLimit("max_connections", 250);
        });

        System.out.println("V2 host: " + manager.getCurrent().getProperty("db_host"));
        manager.rollback();
        System.out.println("Rolled back host: " + manager.getCurrent().getProperty("db_host"));
    }
}
