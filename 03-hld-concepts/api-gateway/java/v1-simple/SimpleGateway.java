import java.util.HashMap;
import java.util.Map;

/**
 * Interview-scale gateway with routing + simple per-route throttling.
 */
public class SimpleGateway {
    private static final class RouteConfig {
        private final String backendUrl;
        private final boolean authRequired;
        private final int maxRequests;
        private int usedRequests;

        private RouteConfig(String backendUrl, boolean authRequired, int maxRequests) {
            this.backendUrl = backendUrl;
            this.authRequired = authRequired;
            this.maxRequests = maxRequests;
            this.usedRequests = 0;
        }
    }

    private final Map<String, RouteConfig> routes = new HashMap<>();

    public void addRoute(String prefix, String backendUrl, boolean authRequired, int maxRequests) {
        routes.put(prefix, new RouteConfig(backendUrl, authRequired, maxRequests));
    }

    public String handle(String path, boolean isAuthenticated) {
        for (Map.Entry<String, RouteConfig> entry : routes.entrySet()) {
            if (!path.startsWith(entry.getKey())) {
                continue;
            }
            RouteConfig route = entry.getValue();
            if (route.authRequired && !isAuthenticated) {
                return "401 Unauthorized";
            }
            if (route.usedRequests >= route.maxRequests) {
                return "429 Too Many Requests";
            }
            route.usedRequests++;
            return "200 Forward -> " + route.backendUrl;
        }
        return "404 Not Found";
    }

    public static void main(String[] args) {
        SimpleGateway gateway = new SimpleGateway();
        gateway.addRoute("/users", "http://user-service:8080", true, 2);
        System.out.println(gateway.handle("/users/1", false));
        System.out.println(gateway.handle("/users/1", true));
        System.out.println(gateway.handle("/users/2", true));
        System.out.println(gateway.handle("/users/3", true));
    }
}
