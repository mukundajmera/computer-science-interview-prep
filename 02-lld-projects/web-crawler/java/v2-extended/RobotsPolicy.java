package v2_extended;

import java.net.URI;
import java.net.URISyntaxException;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

public class RobotsPolicy {
    private final Map<String, List<String>> disallowed = new HashMap<>();

    public void addRule(String host, String path) {
        disallowed.computeIfAbsent(host.toLowerCase(), k -> new ArrayList<>()).add(path);
    }

    public boolean isAllowed(String urlStr) {
        try {
            URI uri = new URI(urlStr);
            String host = uri.getHost() != null ? uri.getHost().toLowerCase() : "";
            String path = uri.getPath() != null ? uri.getPath() : "";
            
            List<String> paths = disallowed.get(host);
            if (paths != null) {
                for (String p : paths) {
                    if (path.startsWith(p)) {
                        return false;
                    }
                }
            }
            return true;
        } catch (URISyntaxException e) {
            return true;
        }
    }
}
