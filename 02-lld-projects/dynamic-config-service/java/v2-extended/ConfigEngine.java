import java.util.HashMap;
import java.util.Map;

public class ConfigEngine {
    private final Map<String, FeatureFlag> flags = new HashMap<>();

    public void updateFlag(FeatureFlag flag) {
        flags.put(flag.getKey(), flag);
    }

    public Variant evaluate(String flagKey, UserContext context) {
        FeatureFlag flag = flags.get(flagKey);
        if (flag != null) {
            return flag.evaluate(context);
        }
        return new Variant(null); // Return empty variant if flag not found
    }
}
