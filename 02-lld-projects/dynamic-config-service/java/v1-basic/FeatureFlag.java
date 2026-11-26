import java.util.Map;
public class FeatureFlag {
    private final String key;
    private final Variant variant;
    private final int rolloutPercentage;
    private final Map<String, Variant> tenantOverrides;
    public FeatureFlag(String key, Variant variant, int rolloutPercentage, Map<String, Variant> tenantOverrides) {
        this.key = key; this.variant = variant; this.rolloutPercentage = rolloutPercentage; this.tenantOverrides = tenantOverrides;
    }
    public String getKey() { return key; }
    public Variant getVariant() { return variant; }
    public int getRolloutPercentage() { return rolloutPercentage; }
    public Map<String, Variant> getTenantOverrides() { return tenantOverrides; }
}
