package v2_extended;

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
        public Map<String, Object> attributes = new HashMap<>();
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
        default Response preFilter(Request request) { return null; }
        default Response postFilter(Request request, Response response) { return response; }
    }

    public static class AuthFilter implements Filter {
        @Override
        public Response preFilter(Request request) {
            if (!request.headers.containsKey("Authorization")) {
                return new Response(401, new HashMap<>(), "Unauthorized");
            }
            return null;
        }
    }

    public static class RateLimitFilter implements Filter {
        private final int maxRequests;
        private final long windowMillis;
        private final Map<String, List<Long>> requests = new HashMap<>();

        public RateLimitFilter(int maxRequests, int windowSec) {
            this.maxRequests = maxRequests;
            this.windowMillis = windowSec * 1000L;
        }

        @Override
        public Response preFilter(Request request) {
            String clientId = request.headers.getOrDefault("Client-ID", "unknown");
            long now = System.currentTimeMillis();

            requests.putIfAbsent(clientId, new ArrayList<>());
            List<Long> clientRequests = requests.get(clientId);

            clientRequests.removeIf(t -> now - t >= windowMillis);

            if (clientRequests.size() >= maxRequests) {
                return new Response(429, new HashMap<>(), "Too Many Requests");
            }

            clientRequests.add(now);
            return null;
        }
    }

    public static class LoggingFilter implements Filter {
        public final List<String> logs = new ArrayList<>();

        @Override
        public Response preFilter(Request request) {
            request.attributes.put("startTime", System.currentTimeMillis());
            return null;
        }

        @Override
        public Response postFilter(Request request, Response response) {
            long startTime = (long) request.attributes.getOrDefault("startTime", System.currentTimeMillis());
            long duration = System.currentTimeMillis() - startTime;
            logs.add(request.method + " " + request.path + " " + response.statusCode + " " + duration + "ms");
            return response;
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
    private final List<Filter> filters = new ArrayList<>();
    private final Map<String, Function<Request, Response>> backends = new HashMap<>();

    public void addRoute(String prefix, String target) {
        routes.add(new Route(prefix, target));
    }

    public void addFilter(Filter filter) {
        filters.add(filter);
    }

    public void registerBackend(String target, Function<Request, Response> handler) {
        backends.put(target, handler);
    }

    public Response handle(Request request) {
        if (request.body != null && request.body.toString().length() > 1024 * 1024) {
            return new Response(413, new HashMap<>(), "Payload Too Large");
        }

        // 1. Execute Pre-filters
        int filterIndex = 0;
        for (Filter filter : filters) {
            Response response = filter.preFilter(request);
            if (response != null) {
                return applyPostFilters(request, response, filterIndex);
            }
            filterIndex++;
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
            return applyPostFilters(request, new Response(404, new HashMap<>(), "Not Found"), filters.size());
        }

        // 3. Backend dispatching
        Function<Request, Response> backend = backends.get(matchedRoute.target);
        if (backend == null) {
            return applyPostFilters(request, new Response(503, new HashMap<>(), "Service Unavailable"), filters.size());
        }

        if (request.isCancelled) {
            return applyPostFilters(request, new Response(499, new HashMap<>(), "Client Closed Request"), filters.size());
        }

        if (request.deadlineMs > 0 && System.currentTimeMillis() > request.deadlineMs) {
            return applyPostFilters(request, new Response(504, new HashMap<>(), "Gateway Timeout"), filters.size());
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
                return applyPostFilters(request, res, filters.size());
            } catch (Exception e) {
                if (attempt == maxAttempts) {
                    return applyPostFilters(request, new Response(500, new HashMap<>(), "Internal Server Error"), filters.size());
                }
            }
        }
        
        return applyPostFilters(request, new Response(500, new HashMap<>(), "Internal Server Error"), filters.size());
    }

    private Response applyPostFilters(Request request, Response response, int startIndex) {
        // According to AC: If a pre-filter short circuits, only the corresponding 
        // post-filters (for the filter that short-circuited and any preceding filters)
        // should be executed. But wait, if pre2 returns a response, post2 doesn't execute?
        // Let's modify: `startIndex - 1` when short-circuited.
        // The original code passed `filterIndex` to applyPostFilters.
        // Wait, if preFilter 2 returns response, filterIndex is 1.
        // So applyPostFilters should run for index 1, 0? Or just 0?
        // "post2 should NOT be called because pre2 returned response"
        // This means we should start from `startIndex - 1`.
        
        for (int i = startIndex - 1; i >= 0; i--) {
            if (i < filters.size()) {
                response = filters.get(i).postFilter(request, response);
            }
        }
        return response;
    }
}
