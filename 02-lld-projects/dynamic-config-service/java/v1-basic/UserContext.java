import java.util.Map;
import java.util.HashMap;
public class UserContext {
    private final String userId;
    private final Map<String, String> attributes = new HashMap<>();
    public UserContext(String userId) { this.userId = userId; }
    public String getUserId() { return userId; }
    public void setAttribute(String key, String value) { attributes.put(key, value); }
    public String getAttribute(String key) { return attributes.get(key); }
}
