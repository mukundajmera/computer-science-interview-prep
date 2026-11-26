import java.util.Map;
public class ConfigSnapshot {
    private final int version;
    private final Map<String, FeatureFlag> flags;
    public ConfigSnapshot(int version, Map<String, FeatureFlag> flags) {
        this.version = version; this.flags = flags;
    }
    public int getVersion() { return version; }
    public Map<String, FeatureFlag> getFlags() { return flags; }
}
