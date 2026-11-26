package v2_extended;

import java.net.URI;
import java.net.URISyntaxException;
import java.util.HashMap;
import java.util.Map;

public class PolitenessPolicy {
    private final long delayMs;
    private final Map<String, Long> lastAccess = new HashMap<>();

    public PolitenessPolicy(long delayMs) {
        this.delayMs = delayMs;
    }

    public void waitForHost(String urlStr) {
        try {
            URI uri = new URI(urlStr);
            String host = uri.getHost();
            if (host == null) return;
            
            long now = System.currentTimeMillis();
            if (lastAccess.containsKey(host)) {
                long elapsed = now - lastAccess.get(host);
                if (elapsed < delayMs) {
                    try {
                        Thread.sleep(delayMs - elapsed);
                    } catch (InterruptedException e) {
                        Thread.currentThread().interrupt();
                    }
                }
            }
            lastAccess.put(host, System.currentTimeMillis());
        } catch (URISyntaxException e) {
            // Ignore
        }
    }
}
