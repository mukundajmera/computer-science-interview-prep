/**
 * URL Shortener - V1 Basic
 * 
 * HTTP Controller/Handler layer for URL shortening API.
 * Framework-agnostic implementation.
 */

import java.util.HashMap;
import java.util.Map;
import java.util.Optional;

/**
 * HTTP Request abstraction.
 */
class HttpRequest {
    private final String method;
    private final String path;
    private final Map<String, String> headers;
    private final Map<String, Object> body;
    private final Map<String, String> pathParams;
    private final Map<String, String> queryParams;
    
    public HttpRequest(String method, String path) {
        this.method = method;
        this.path = path;
        this.headers = new HashMap<>();
        this.body = new HashMap<>();
        this.pathParams = new HashMap<>();
        this.queryParams = new HashMap<>();
    }
    
    public String getMethod() { return method; }
    public String getPath() { return path; }
    public Map<String, String> getHeaders() { return headers; }
    public Map<String, Object> getBody() { return body; }
    public Map<String, String> getPathParams() { return pathParams; }
    public String getPathParam(String name) { return pathParams.get(name); }
    public String getQueryParam(String name) { return queryParams.get(name); }
    public Object getBodyField(String name) { return body.get(name); }
}

/**
 * HTTP Response abstraction.
 */
class HttpResponse {
    private int statusCode;
    private final Map<String, String> headers;
    private Object body;
    
    public HttpResponse() {
        this.statusCode = 200;
        this.headers = new HashMap<>();
    }
    
    public static HttpResponse ok(Object body) {
        HttpResponse response = new HttpResponse();
        response.statusCode = 200;
        response.body = body;
        return response;
    }
    
    public static HttpResponse created(Object body) {
        HttpResponse response = new HttpResponse();
        response.statusCode = 201;
        response.body = body;
        return response;
    }
    
    public static HttpResponse redirect(String location) {
        HttpResponse response = new HttpResponse();
        response.statusCode = 301;
        response.headers.put("Location", location);
        return response;
    }
    
    public static HttpResponse notFound(String message) {
        HttpResponse response = new HttpResponse();
        response.statusCode = 404;
        response.body = Map.of("error", message);
        return response;
    }
    
    public static HttpResponse conflict(String message) {
        HttpResponse response = new HttpResponse();
        response.statusCode = 409;
        response.body = Map.of("error", message);
        return response;
    }
    
    public static HttpResponse badRequest(String message) {
        HttpResponse response = new HttpResponse();
        response.statusCode = 400;
        response.body = Map.of("error", message);
        return response;
    }
    
    public static HttpResponse gone(String message) {
        HttpResponse response = new HttpResponse();
        response.statusCode = 410;
        response.body = Map.of("error", message);
        return response;
    }
    
    public static HttpResponse noContent() {
        HttpResponse response = new HttpResponse();
        response.statusCode = 204;
        return response;
    }
    
    public int getStatusCode() { return statusCode; }
    public Map<String, String> getHeaders() { return headers; }
    public Object getBody() { return body; }
}

/**
 * URL Controller handling HTTP requests.
 * Routes:
 *   POST /api/v1/urls         - Create short URL
 *   GET  /{shortCode}         - Redirect to original URL
 *   GET  /api/v1/urls/{code}/stats - Get URL statistics
 *   DELETE /api/v1/urls/{code}     - Delete URL
 */
class UrlController {
    
    private final UrlShorteningService urlService;
    
    public UrlController(UrlShorteningService urlService) {
        this.urlService = urlService;
    }
    
    /**
     * POST /api/v1/urls
     * Create a new short URL.
     */
    public HttpResponse createShortUrl(HttpRequest request) {
        try {
            String longUrl = (String) request.getBodyField("longUrl");
            String customAlias = (String) request.getBodyField("customAlias");
            String expiresAtStr = (String) request.getBodyField("expiresAt");
            
            if (longUrl == null || longUrl.isEmpty()) {
                return HttpResponse.badRequest("longUrl is required");
            }
            
            java.time.Instant expiresAt = null;
            if (expiresAtStr != null) {
                expiresAt = java.time.Instant.parse(expiresAtStr);
            }
            
            CreateUrlRequest createRequest = new CreateUrlRequest(
                longUrl, customAlias, expiresAt, null
            );
            
            CreateUrlResponse response = urlService.createShortUrl(createRequest);
            
            return HttpResponse.created(Map.of(
                "shortUrl", response.getShortUrl(),
                "shortCode", response.getShortCode(),
                "longUrl", response.getLongUrl(),
                "createdAt", response.getCreatedAt().toString(),
                "expiresAt", response.getExpiresAt() != null ? 
                    response.getExpiresAt().toString() : null
            ));
            
        } catch (AliasAlreadyExistsException e) {
            return HttpResponse.conflict(e.getMessage());
        } catch (IllegalArgumentException e) {
            return HttpResponse.badRequest(e.getMessage());
        }
    }
    
    /**
     * GET /{shortCode}
     * Redirect to the original URL.
     */
    public HttpResponse redirect(HttpRequest request) {
        String shortCode = request.getPathParam("shortCode");
        
        if (shortCode == null || shortCode.isEmpty()) {
            return HttpResponse.badRequest("Short code is required");
        }
        
        try {
            Optional<String> originalUrl = urlService.getOriginalUrl(shortCode);
            
            if (originalUrl.isEmpty()) {
                return HttpResponse.notFound("URL not found: " + shortCode);
            }
            
            return HttpResponse.redirect(originalUrl.get());
            
        } catch (UrlExpiredException e) {
            return HttpResponse.gone(e.getMessage());
        }
    }
    
    /**
     * GET /api/v1/urls/{shortCode}/stats
     * Get URL statistics.
     */
    public HttpResponse getStats(HttpRequest request) {
        String shortCode = request.getPathParam("shortCode");
        
        Optional<UrlStats> stats = urlService.getStats(shortCode);
        
        if (stats.isEmpty()) {
            return HttpResponse.notFound("URL not found: " + shortCode);
        }
        
        UrlStats s = stats.get();
        return HttpResponse.ok(Map.of(
            "shortCode", s.getShortCode(),
            "longUrl", s.getLongUrl(),
            "clicks", s.getClickCount(),
            "createdAt", s.getCreatedAt().toString(),
            "expiresAt", s.getExpiresAt() != null ? s.getExpiresAt().toString() : null
        ));
    }
    
    /**
     * DELETE /api/v1/urls/{shortCode}
     * Delete a short URL.
     */
    public HttpResponse deleteUrl(HttpRequest request) {
        String shortCode = request.getPathParam("shortCode");
        
        boolean deleted = urlService.deleteUrl(shortCode);
        
        if (!deleted) {
            return HttpResponse.notFound("URL not found: " + shortCode);
        }
        
        return HttpResponse.noContent();
    }
}
