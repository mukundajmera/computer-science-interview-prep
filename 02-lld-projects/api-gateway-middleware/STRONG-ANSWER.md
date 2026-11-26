# Strong Answer: API Gateway & Middleware Pipeline

A strong candidate will immediately recognize this as an application of the **Chain of Responsibility** pattern and will structure their solution cleanly, prioritizing standard libraries and focusing on thread safety.

Below is an example of what an excellent standard-library-only bounded simulator implementation looks like in Java and Python. It explicitly demonstrates the Filter Chain Model and a failure invariant (Circuit Breaker OPEN state).

## Java Implementation

```java
import java.util.*;
import java.util.concurrent.atomic.AtomicInteger;

// 1. Context Objects
class RequestContext {
    public final String path;
    public final Map<String, String> headers;
    
    public RequestContext(String path, Map<String, String> headers) {
        this.path = path;
        this.headers = headers != null ? headers : new HashMap<>();
    }
}

class ResponseContext {
    public int statusCode = 200;
    public String body = "";
}

class HttpContext {
    public final RequestContext request;
    public final ResponseContext response;

    public HttpContext(RequestContext request) {
        this.request = request;
        this.response = new ResponseContext();
    }
}

// 2. Filter & Target Abstractions
interface Filter {
    void doFilter(HttpContext context, FilterChain chain) throws Exception;
}

interface FilterChain {
    void doFilter(HttpContext context) throws Exception;
}

interface TargetHandler {
    void execute(HttpContext context) throws Exception;
}

// 3. Engine Implementation
class GatewayFilterChain implements FilterChain {
    private final List<Filter> filters;
    private final TargetHandler target;
    private int index = 0;

    public GatewayFilterChain(List<Filter> filters, TargetHandler target) {
        this.filters = filters;
        this.target = target;
    }

    @Override
    public void doFilter(HttpContext context) throws Exception {
        if (index < filters.size()) {
            Filter filter = filters.get(index++);
            filter.doFilter(context, this);
        } else {
            target.execute(context);
        }
    }
}

class ApiGateway {
    private final List<Filter> globalFilters = new ArrayList<>();
    private final Map<String, TargetHandler> routes = new HashMap<>();

    public void addFilter(Filter f) { globalFilters.add(f); }
    public void addRoute(String path, TargetHandler t) { routes.put(path, t); }

    public ResponseContext handle(RequestContext request) {
        HttpContext ctx = new HttpContext(request);
        try {
            TargetHandler target = routes.get(request.path);
            if (target == null) {
                ctx.response.statusCode = 404;
                ctx.response.body = "Not Found";
                return ctx.response;
            }
            
            FilterChain chain = new GatewayFilterChain(globalFilters, target);
            chain.doFilter(ctx);
            
        } catch (Exception e) {
            ctx.response.statusCode = 500;
            ctx.response.body = "Internal Server Error";
        }
        return ctx.response;
    }
}

// 4. Concrete Filters & Invariant Mapping

// Demonstrates Short-Circuiting
class AuthFilter implements Filter {
    @Override
    public void doFilter(HttpContext context, FilterChain chain) throws Exception {
        if (!"valid-token".equals(context.request.headers.get("Authorization"))) {
            context.response.statusCode = 401;
            context.response.body = "Unauthorized";
            return; // Short-circuit, do not call chain.doFilter()
        }
        chain.doFilter(context);
    }
}

// Demonstrates Failure Invariant: Circuit Breaker OPEN state
class CircuitBreakerFilter implements Filter {
    private final int threshold;
    private final AtomicInteger failures = new AtomicInteger(0);

    public CircuitBreakerFilter(int threshold) {
        this.threshold = threshold;
    }

    @Override
    public void doFilter(HttpContext context, FilterChain chain) throws Exception {
        if (failures.get() >= threshold) {
            // Invariant Map: Circuit Breaker OPEN state halts chain
            context.response.statusCode = 503;
            context.response.body = "Service Unavailable - Circuit Open";
            return; 
        }

        try {
            chain.doFilter(context);
            // If target returns 5xx, treat as failure
            if (context.response.statusCode >= 500) {
                failures.incrementAndGet();
            } else {
                failures.set(0); // Reset on success
            }
        } catch (Exception e) {
            failures.incrementAndGet();
            throw e; // rethrow for gateway to catch
        }
    }
}

// Test Fixture
public class ApiGatewaySimulation {
    public static void main(String[] args) {
        ApiGateway gateway = new ApiGateway();
        gateway.addFilter(new AuthFilter());
        gateway.addFilter(new CircuitBreakerFilter(2));
        
        TargetHandler flakyTarget = ctx -> {
            ctx.response.statusCode = 500;
            ctx.response.body = "Backend Crash";
        };
        gateway.addRoute("/api/flaky", flakyTarget);

        // Test Auth Short-Circuit
        RequestContext noAuth = new RequestContext("/api/flaky", null);
        assert gateway.handle(noAuth).statusCode == 401;

        // Test Circuit Breaker invariant
        Map<String, String> authHeaders = new HashMap<>();
        authHeaders.put("Authorization", "valid-token");
        RequestContext req = new RequestContext("/api/flaky", authHeaders);

        assert gateway.handle(req).statusCode == 500; // Fail 1
        assert gateway.handle(req).statusCode == 500; // Fail 2 (Threshold reached)
        assert gateway.handle(req).statusCode == 503; // Circuit OPEN
        
        System.out.println("All Gateway constraints passed!");
    }
}
```

## Python Implementation

```python
import typing

# 1. Context Objects
class RequestContext:
    def __init__(self, path: str, headers: dict = None):
        self.path = path
        self.headers = headers or {}

class ResponseContext:
    def __init__(self):
        self.status_code = 200
        self.body = ""

class HttpContext:
    def __init__(self, request: RequestContext):
        self.request = request
        self.response = ResponseContext()

# 2. Filter & Target Abstractions
class FilterChain:
    def __init__(self, filters: list, target):
        self.filters = filters
        self.target = target
        self.index = 0

    def do_filter(self, context: HttpContext):
        if self.index < len(self.filters):
            current_filter = self.filters[self.index]
            self.index += 1
            current_filter.do_filter(context, self)
        else:
            self.target(context)

# 3. Engine Implementation
class ApiGateway:
    def __init__(self):
        self.global_filters = []
        self.routes = {}

    def add_filter(self, f):
        self.global_filters.append(f)

    def add_route(self, path: str, handler):
        self.routes[path] = handler

    def handle(self, request: RequestContext) -> ResponseContext:
        ctx = HttpContext(request)
        try:
            target = self.routes.get(request.path)
            if not target:
                ctx.response.status_code = 404
                ctx.response.body = "Not Found"
                return ctx.response
            
            chain = FilterChain(self.global_filters, target)
            chain.do_filter(ctx)
        except Exception:
            ctx.response.status_code = 500
            ctx.response.body = "Internal Server Error"
            
        return ctx.response

# 4. Concrete Filters & Invariant Mapping

# Demonstrates Short-Circuiting
class AuthFilter:
    def do_filter(self, context: HttpContext, chain: FilterChain):
        if context.request.headers.get("Authorization") != "valid-token":
            context.response.status_code = 401
            context.response.body = "Unauthorized"
            return # Short-circuit
        chain.do_filter(context)

# Demonstrates Failure Invariant: Circuit Breaker OPEN state
import threading

class CircuitBreakerFilter:
    def __init__(self, threshold: int):
        self.threshold = threshold
        self.failures = 0
        self.lock = threading.Lock()

    def do_filter(self, context: HttpContext, chain: FilterChain):
        with self.lock:
            if self.failures >= self.threshold:
                # Invariant Map: Circuit Breaker OPEN state halts chain
                context.response.status_code = 503
                context.response.body = "Service Unavailable - Circuit Open"
                return
                
        try:
            chain.do_filter(context)
            with self.lock:
                if context.response.status_code >= 500:
                    self.failures += 1
                else:
                    self.failures = 0
        except Exception as e:
            with self.lock:
                self.failures += 1
            raise e

# Test Fixture
if __name__ == "__main__":
    gateway = ApiGateway()
    gateway.add_filter(AuthFilter())
    gateway.add_filter(CircuitBreakerFilter(threshold=2))
    
    def flaky_target(ctx: HttpContext):
        ctx.response.status_code = 500
        ctx.response.body = "Backend Crash"
        
    gateway.add_route("/api/flaky", flaky_target)
    
    # Test Auth Short-Circuit
    assert gateway.handle(RequestContext("/api/flaky")).status_code == 401
    
    # Test Circuit Breaker Invariant
    req = RequestContext("/api/flaky", {"Authorization": "valid-token"})
    assert gateway.handle(req).status_code == 500 # Fail 1
    assert gateway.handle(req).status_code == 500 # Fail 2 (Threshold reached)
    assert gateway.handle(req).status_code == 503 # Circuit OPEN
    
    print("All Gateway constraints passed!")
```