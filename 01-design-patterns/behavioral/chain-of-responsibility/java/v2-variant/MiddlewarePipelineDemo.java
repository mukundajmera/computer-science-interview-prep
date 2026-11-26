package chainofresponsibility.v2;

import java.util.HashMap;
import java.util.Map;

/**
 * v2-variant: Chain of Responsibility Pattern for HTTP Middleware Pipelines.
 * Demonstrates request interceptors (Authentication, Rate-Limiting, Payload Sanitization)
 * with short-circuit capabilities when validation fails.
 */
public class MiddlewarePipelineDemo {

    public static class HttpRequest {
        private final String path;
        private final String token;
        private final String body;
        private final String clientIp;

        public HttpRequest(String path, String token, String body, String clientIp) {
            this.path = path;
            this.token = token;
            this.body = body;
            this.clientIp = clientIp;
        }

        public String getPath() {
            return path;
        }

        public String getToken() {
            return token;
        }

        public String getBody() {
            return body;
        }

        public String getClientIp() {
            return clientIp;
        }
    }

    public static class HttpResponse {
        private final int statusCode;
        private final String message;

        public HttpResponse(int statusCode, String message) {
            this.statusCode = statusCode;
            this.message = message;
        }

        public int getStatusCode() {
            return statusCode;
        }

        public String getMessage() {
            return message;
        }

        public boolean isSuccess() {
            return statusCode >= 200 && statusCode < 300;
        }
    }

    public abstract static class Middleware {
        private Middleware next;

        public Middleware linkWith(Middleware next) {
            this.next = next;
            return next;
        }

        public abstract HttpResponse handle(HttpRequest request);

        protected HttpResponse checkNext(HttpRequest request) {
            if (next == null) {
                return new HttpResponse(200, "OK: Request processed successfully");
            }
            return next.handle(request);
        }
    }

    public static class AuthMiddleware extends Middleware {
        @Override
        public HttpResponse handle(HttpRequest request) {
            if (request.getToken() == null || !request.getToken().startsWith("Bearer ")) {
                return new HttpResponse(401, "Unauthorized: Missing or invalid bearer token");
            }
            return checkNext(request);
        }
    }

    public static class RateLimitMiddleware extends Middleware {
        private final int maxPerMinute;
        private final Map<String, Integer> requestCounts = new HashMap<>();

        public RateLimitMiddleware(int maxPerMinute) {
            this.maxPerMinute = maxPerMinute;
        }

        @Override
        public HttpResponse handle(HttpRequest request) {
            String ip = request.getClientIp();
            int current = requestCounts.getOrDefault(ip, 0) + 1;
            requestCounts.put(ip, current);

            if (current > maxPerMinute) {
                return new HttpResponse(429, "Too Many Requests: Rate limit exceeded");
            }
            return checkNext(request);
        }
    }

    public static class SanitizationMiddleware extends Middleware {
        @Override
        public HttpResponse handle(HttpRequest request) {
            if (request.getBody() != null && request.getBody().contains("<script>")) {
                return new HttpResponse(400, "Bad Request: Malicious script tags detected");
            }
            return checkNext(request);
        }
    }

    public static void main(String[] args) {
        Middleware pipeline = new AuthMiddleware();
        pipeline.linkWith(new RateLimitMiddleware(2))
                .linkWith(new SanitizationMiddleware());

        HttpRequest valid = new HttpRequest("/api/data", "Bearer valid_tok", "hello", "10.0.0.1");
        HttpResponse res1 = pipeline.handle(valid);
        System.out.println("Valid request: " + res1.getStatusCode() + " - " + res1.getMessage());

        HttpRequest malicious = new HttpRequest("/api/data", "Bearer valid_tok", "<script>alert(1)</script>", "10.0.0.1");
        HttpResponse res2 = pipeline.handle(malicious);
        System.out.println("Malicious request: " + res2.getStatusCode() + " - " + res2.getMessage());
    }
}
