/**
 * Decorator Pattern - V3 Advanced: HTTP Middleware
 * 
 * Real-world example showing how web frameworks use decorator pattern
 * for request/response middleware (authentication, logging, caching).
 */

import java.util.*;

// Request and Response objects
class HttpRequest {
    private String method;
    private String path;
    private Map<String, String> headers;
    private String body;
    private Map<String, Object> attributes;
    
    public HttpRequest(String method, String path) {
        this.method = method;
        this.path = path;
        this.headers = new HashMap<>();
        this.attributes = new HashMap<>();
    }
    
    public String getMethod() { return method; }
    public String getPath() { return path; }
    public String getHeader(String name) { return headers.get(name); }
    public void setHeader(String name, String value) { headers.put(name, value); }
    public Object getAttribute(String name) { return attributes.get(name); }
    public void setAttribute(String name, Object value) { attributes.put(name, value); }
    public String getBody() { return body; }
    public void setBody(String body) { this.body = body; }
}

class HttpResponse {
    private int statusCode;
    private Map<String, String> headers;
    private String body;
    
    public HttpResponse() {
        this.statusCode = 200;
        this.headers = new HashMap<>();
    }
    
    public int getStatusCode() { return statusCode; }
    public void setStatusCode(int code) { this.statusCode = code; }
    public String getHeader(String name) { return headers.get(name); }
    public void setHeader(String name, String value) { headers.put(name, value); }
    public String getBody() { return body; }
    public void setBody(String body) { this.body = body; }
}

// Component Interface - Request Handler
interface RequestHandler {
    HttpResponse handle(HttpRequest request);
}

// Concrete Component - Core Application Handler
class ApplicationHandler implements RequestHandler {
    @Override
    public HttpResponse handle(HttpRequest request) {
        HttpResponse response = new HttpResponse();
        
        // Simulate application logic
        if ("/api/users".equals(request.getPath())) {
            response.setBody("{\"users\": [{\"id\": 1, \"name\": \"Alice\"}]}");
            response.setHeader("Content-Type", "application/json");
        } else if ("/api/protected".equals(request.getPath())) {
            // Check if authenticated (set by middleware)
            Object user = request.getAttribute("user");
            if (user != null) {
                response.setBody("{\"message\": \"Welcome, " + user + "!\"}");
            } else {
                response.setStatusCode(401);
                response.setBody("{\"error\": \"Unauthorized\"}");
            }
        } else {
            response.setStatusCode(404);
            response.setBody("{\"error\": \"Not Found\"}");
        }
        
        return response;
    }
}

// Abstract Decorator - Middleware Base
abstract class Middleware implements RequestHandler {
    protected RequestHandler next;
    
    public Middleware(RequestHandler next) {
        this.next = next;
    }
}

// Concrete Decorator - Logging Middleware
class LoggingMiddleware extends Middleware {
    public LoggingMiddleware(RequestHandler next) {
        super(next);
    }
    
    @Override
    public HttpResponse handle(HttpRequest request) {
        long startTime = System.currentTimeMillis();
        System.out.println("[LOG] " + request.getMethod() + " " + request.getPath());
        
        HttpResponse response = next.handle(request);
        
        long duration = System.currentTimeMillis() - startTime;
        System.out.println("[LOG] Response: " + response.getStatusCode() + " (" + duration + "ms)");
        
        return response;
    }
}

// Concrete Decorator - Authentication Middleware
class AuthenticationMiddleware extends Middleware {
    private Set<String> validTokens;
    
    public AuthenticationMiddleware(RequestHandler next) {
        super(next);
        this.validTokens = Set.of("valid-token-123", "admin-token-456");
    }
    
    @Override
    public HttpResponse handle(HttpRequest request) {
        String authHeader = request.getHeader("Authorization");
        
        if (authHeader != null && authHeader.startsWith("Bearer ")) {
            String token = authHeader.substring(7);
            if (validTokens.contains(token)) {
                request.setAttribute("user", "AuthenticatedUser");
                request.setAttribute("authenticated", true);
            }
        }
        
        return next.handle(request);
    }
}

// Concrete Decorator - Rate Limiting Middleware
class RateLimitMiddleware extends Middleware {
    private Map<String, Integer> requestCounts = new HashMap<>();
    private int maxRequests = 5;
    
    public RateLimitMiddleware(RequestHandler next) {
        super(next);
    }
    
    @Override
    public HttpResponse handle(HttpRequest request) {
        String clientIp = request.getHeader("X-Client-IP");
        if (clientIp == null) clientIp = "unknown";
        
        int count = requestCounts.getOrDefault(clientIp, 0) + 1;
        requestCounts.put(clientIp, count);
        
        if (count > maxRequests) {
            HttpResponse response = new HttpResponse();
            response.setStatusCode(429);
            response.setBody("{\"error\": \"Too Many Requests\"}");
            response.setHeader("Retry-After", "60");
            System.out.println("[RATE LIMIT] Blocked: " + clientIp);
            return response;
        }
        
        return next.handle(request);
    }
}

// Concrete Decorator - Caching Middleware
class CachingMiddleware extends Middleware {
    private Map<String, HttpResponse> cache = new HashMap<>();
    
    public CachingMiddleware(RequestHandler next) {
        super(next);
    }
    
    @Override
    public HttpResponse handle(HttpRequest request) {
        // Only cache GET requests
        if (!"GET".equals(request.getMethod())) {
            return next.handle(request);
        }
        
        String cacheKey = request.getPath();
        if (cache.containsKey(cacheKey)) {
            System.out.println("[CACHE] Hit: " + cacheKey);
            HttpResponse cached = cache.get(cacheKey);
            cached.setHeader("X-Cache", "HIT");
            return cached;
        }
        
        System.out.println("[CACHE] Miss: " + cacheKey);
        HttpResponse response = next.handle(request);
        
        if (response.getStatusCode() == 200) {
            cache.put(cacheKey, response);
        }
        response.setHeader("X-Cache", "MISS");
        
        return response;
    }
}

// Demo
public class MiddlewareDemo {
    public static void main(String[] args) {
        // Build middleware stack (order matters!)
        RequestHandler handler = new LoggingMiddleware(
            new RateLimitMiddleware(
                new CachingMiddleware(
                    new AuthenticationMiddleware(
                        new ApplicationHandler()
                    )
                )
            )
        );
        
        // Request 1: Simple GET
        System.out.println("=== Request 1: GET /api/users ===");
        HttpRequest req1 = new HttpRequest("GET", "/api/users");
        req1.setHeader("X-Client-IP", "192.168.1.1");
        HttpResponse res1 = handler.handle(req1);
        System.out.println("Body: " + res1.getBody());
        
        // Request 2: Same request (should hit cache)
        System.out.println("\n=== Request 2: GET /api/users (cached) ===");
        HttpRequest req2 = new HttpRequest("GET", "/api/users");
        req2.setHeader("X-Client-IP", "192.168.1.1");
        HttpResponse res2 = handler.handle(req2);
        System.out.println("Cache: " + res2.getHeader("X-Cache"));
        
        // Request 3: Protected endpoint without auth
        System.out.println("\n=== Request 3: GET /api/protected (no auth) ===");
        HttpRequest req3 = new HttpRequest("GET", "/api/protected");
        req3.setHeader("X-Client-IP", "192.168.1.2");
        HttpResponse res3 = handler.handle(req3);
        System.out.println("Status: " + res3.getStatusCode());
        
        // Request 4: Protected endpoint with auth
        System.out.println("\n=== Request 4: GET /api/protected (with auth) ===");
        HttpRequest req4 = new HttpRequest("GET", "/api/protected");
        req4.setHeader("X-Client-IP", "192.168.1.2");
        req4.setHeader("Authorization", "Bearer valid-token-123");
        HttpResponse res4 = handler.handle(req4);
        System.out.println("Body: " + res4.getBody());
    }
}
