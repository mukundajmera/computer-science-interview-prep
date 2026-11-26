package v1_basic;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.function.Function;

public class ApiGateway {

    public static class Request {
        public String path;
        public String method;
        public Map<String, String> headers;
        public Object body;
        public long deadlineMs;
        public boolean isCancelled;

        public Request(String path, String method, Map<String, String> headers, Object body) {
            this.path = path;
            this.method = method;
            this.headers = headers != null ? headers : new HashMap<>();
            this.body = body;
        }
    }

    public static class Response {
        public int statusCode;
        public Map<String, String> headers;
        public Object body;

        public Response(int statusCode, Map<String, String> headers, Object body) {
            this.statusCode = statusCode;
            this.headers = headers != null ? headers : new HashMap<>();
            this.body = body;
        }
    }

    public interface Filter {
        Response filter(Request request);
    }

    public static class AuthFilter implements Filter {
        @Override
        public Response filter(Request request) {
            if (!request.headers.containsKey("Authorization")) {
                return new Response(401, new HashMap<>(), "Unauthorized");
            }
            return null;
        }
    }

    private static class Route {
        String prefix;
        String target;

        Route(String prefix, String target) {
            this.prefix = prefix;
            this.target = target;
        }
    }

    private final List<Route> routes = new ArrayList<>();
    private final List<Filter> preFilters = new ArrayList<>();
    private final Map<String, Function<Request, Response>> backends = new HashMap<>();

    public void addRoute(String prefix, String target) {
        routes.add(new Route(prefix, target));
    }

    public void addPreFilter(Filter filter) {
        preFilters.add(filter);
    }

    public void registerBackend(String target, Function<Request, Response> handler) {
        backends.put(target, handler);
    }

    public Response handle(Request request) {
        if (request.body != null && request.body.toString().length() > 1024 * 1024) {
            return new Response(413, new HashMap<>(), "Payload Too Large");
        }

        // 1. Execute Pre-filters
        for (Filter filter : preFilters) {
            Response res = filter.filter(request);
            if (res != null) {
                return res;
            }
        }

        // 2. Route Matching
        Route matchedRoute = null;
        for (Route route : routes) {
            if (request.path.startsWith(route.prefix)) {
                matchedRoute = route;
                break;
            }
        }

        if (matchedRoute == null) {
            return new Response(404, new HashMap<>(), "Not Found");
        }

        // 3. Backend dispatching
        Function<Request, Response> backend = backends.get(matchedRoute.target);
        if (backend == null) {
            return new Response(503, new HashMap<>(), "Service Unavailable");
        }

        if (request.isCancelled) {
            return new Response(499, new HashMap<>(), "Client Closed Request");
        }

        if (request.deadlineMs > 0 && System.currentTimeMillis() > request.deadlineMs) {
            return new Response(504, new HashMap<>(), "Gateway Timeout");
        }

        boolean isIdempotent = "GET".equalsIgnoreCase(request.method) || 
                               (request.headers != null && request.headers.containsKey("Idempotency-Key"));
        int maxAttempts = isIdempotent ? 2 : 1;
        
        for (int attempt = 1; attempt <= maxAttempts; attempt++) {
            try {
                Response res = backend.apply(request);
                if (res.statusCode >= 500 && attempt < maxAttempts) {
                    continue;
                }
                return res;
            } catch (Exception e) {
                if (attempt == maxAttempts) {
                    return new Response(500, new HashMap<>(), "Internal Server Error");
                }
            }
        }
        
        return new Response(500, new HashMap<>(), "Internal Server Error");
    }
}
