package v3_optimized;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.CopyOnWriteArrayList;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.concurrent.atomic.AtomicReference;
import java.util.concurrent.locks.ReentrantLock;
import java.util.function.Function;

public class ApiGateway {

    public static class Request {
        public String path;
        public String method;
        public Map<String, String> headers;
        public Object body;
        public Map<String, Object> attributes = new ConcurrentHashMap<>();

        public Request(String path, String method, Map<String, String> headers, Object body) {
            this.path = path;
            this.method = method;
            this.headers = headers != null ? new ConcurrentHashMap<>(headers) : new ConcurrentHashMap<>();
            this.body = body;
        }
    }

    public static class Response {
        public int statusCode;
        public Map<String, String> headers;
        public Object body;

        public Response(int statusCode, Map<String, String> headers, Object body) {
            this.statusCode = statusCode;
            this.headers = headers != null ? new ConcurrentHashMap<>(headers) : new ConcurrentHashMap<>();
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
        private final Map<String, List<Long>> requests = new ConcurrentHashMap<>();
        private final Map<String, ReentrantLock> clientLocks = new ConcurrentHashMap<>();

        public RateLimitFilter(int maxRequests, int windowSec) {
            this.maxRequests = maxRequests;
            this.windowMillis = windowSec * 1000L;
        }

        @Override
        public Response preFilter(Request request) {
            String clientId = request.headers.getOrDefault("Client-ID", "unknown");
            long now = System.currentTimeMillis();

            ReentrantLock lock = clientLocks.computeIfAbsent(clientId, k -> new ReentrantLock());
            lock.lock();
            try {
                requests.putIfAbsent(clientId, new ArrayList<>());
                List<Long> clientRequests = requests.get(clientId);

                clientRequests.removeIf(t -> now - t >= windowMillis);

                if (clientRequests.size() >= maxRequests) {
                    return new Response(429, new HashMap<>(), "Too Many Requests");
                }

                clientRequests.add(now);
                return null;
            } finally {
                lock.unlock();
            }
        }
    }

    public static class LoggingFilter implements Filter {
        public final List<String> logs = new CopyOnWriteArrayList<>();

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

    public static class CircuitBreaker {
        private final int failureThreshold;
        private final long resetTimeoutMillis;
        private final AtomicInteger failures = new AtomicInteger(0);
        
        public enum State { CLOSED, OPEN, HALF_OPEN }
        private final AtomicReference<State> state = new AtomicReference<>(State.CLOSED);
        private volatile long lastFailureTime = 0;
        private final ReentrantLock lock = new ReentrantLock();

        public CircuitBreaker() {
            this(3, 5); // default: 3 failures, 5 seconds
        }

        public CircuitBreaker(int failureThreshold, int resetTimeoutSec) {
            this.failureThreshold = failureThreshold;
            this.resetTimeoutMillis = resetTimeoutSec * 1000L;
        }

        public boolean allowRequest() {
            State currentState = state.get();
            if (currentState == State.OPEN) {
                if (System.currentTimeMillis() - lastFailureTime > resetTimeoutMillis) {
                    if (state.compareAndSet(State.OPEN, State.HALF_OPEN)) {
                        return true;
                    }
                }
                return false;
            }
            if (currentState == State.HALF_OPEN) {
                return false;
            }
            return true;
        }

        public void recordSuccess() {
            failures.set(0);
            state.set(State.CLOSED);
        }

        public void recordFailure() {
            lock.lock();
            try {
                int count = failures.incrementAndGet();
                if (count >= failureThreshold) {
                    state.set(State.OPEN);
                    lastFailureTime = System.currentTimeMillis();
                } else if (state.get() == State.HALF_OPEN) {
                    state.set(State.OPEN);
                    lastFailureTime = System.currentTimeMillis();
                }
            } finally {
                lock.unlock();
            }
        }
        
        public State getState() {
            return state.get();
        }
        
        public int getFailures() {
            return failures.get();
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

    private final List<Route> routes = new CopyOnWriteArrayList<>();
    private final List<Filter> filters = new CopyOnWriteArrayList<>();
    private final Map<String, Function<Request, Response>> backends = new ConcurrentHashMap<>();
    private final Map<String, CircuitBreaker> circuitBreakers = new ConcurrentHashMap<>();
    
    public Map<String, CircuitBreaker> getCircuitBreakers() {
        return circuitBreakers;
    }

    public void addRoute(String prefix, String target) {
        routes.add(new Route(prefix, target));
        circuitBreakers.putIfAbsent(target, new CircuitBreaker());
    }
    
    public void addRoute(String prefix, String target, CircuitBreaker cb) {
        routes.add(new Route(prefix, target));
        circuitBreakers.put(target, cb);
    }

    public void addFilter(Filter filter) {
        filters.add(filter);
    }

    public void registerBackend(String target, Function<Request, Response> handler) {
        backends.put(target, handler);
    }

    public Response handle(Request request) {
        for (Filter filter : filters) {
            Response response = filter.preFilter(request);
            if (response != null) {
                return applyPostFilters(request, response);
            }
        }

        Route matchedRoute = null;
        for (Route route : routes) {
            if (request.path.startsWith(route.prefix)) {
                matchedRoute = route;
                break;
            }
        }

        if (matchedRoute == null) {
            return applyPostFilters(request, new Response(404, new HashMap<>(), "Not Found"));
        }

        CircuitBreaker cb = circuitBreakers.get(matchedRoute.target);
        if (cb != null && !cb.allowRequest()) {
            return applyPostFilters(request, new Response(503, new HashMap<>(), "Service Unavailable - Circuit Open"));
        }

        Function<Request, Response> backend = backends.get(matchedRoute.target);
        if (backend == null) {
            if (cb != null) cb.recordFailure();
            return applyPostFilters(request, new Response(503, new HashMap<>(), "Service Unavailable"));
        }

        try {
            Response backendRes = backend.apply(request);
            if (backendRes.statusCode >= 500) {
                if (cb != null) cb.recordFailure();
            } else {
                if (cb != null) cb.recordSuccess();
            }
            return applyPostFilters(request, backendRes);
        } catch (Exception e) {
            if (cb != null) cb.recordFailure();
            return applyPostFilters(request, new Response(500, new HashMap<>(), "Internal Server Error"));
        }
    }

    private Response applyPostFilters(Request request, Response response) {
        for (int i = filters.size() - 1; i >= 0; i--) {
            response = filters.get(i).postFilter(request, response);
        }
        return response;
    }
}
