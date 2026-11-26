/**
 * URL Shortener - V1 Basic
 * 
 * Core service implementation for URL shortening.
 */

import java.net.MalformedURLException;
import java.net.URL;
import java.time.Instant;
import java.util.Optional;

/**
 * Basic implementation of URL shortening service.
 * Suitable for low-traffic scenarios without caching.
 */
class BasicUrlShorteningService implements UrlShorteningService {
    
    private final UrlRepository repository;
    private final ShortCodeGenerator codeGenerator;
    private final String baseUrl;
    
    public BasicUrlShorteningService(UrlRepository repository,
                                     ShortCodeGenerator codeGenerator,
                                     String baseUrl) {
        this.repository = repository;
        this.codeGenerator = codeGenerator;
        this.baseUrl = baseUrl;
    }
    
    @Override
    public CreateUrlResponse createShortUrl(CreateUrlRequest request) {
        // Validate URL format
        validateUrl(request.getLongUrl());
        
        String shortCode;
        boolean isCustom = false;
        
        if (request.hasCustomAlias()) {
            // Custom alias requested
            String alias = request.getCustomAlias();
            
            if (!codeGenerator.isValidCustomAlias(alias)) {
                throw new IllegalArgumentException("Invalid custom alias format");
            }
            
            if (repository.existsByShortCode(alias)) {
                throw new AliasAlreadyExistsException("Custom alias already exists: " + alias);
            }
            
            shortCode = alias;
            isCustom = true;
        } else {
            // Generate unique code
            shortCode = codeGenerator.generate();
            
            // Handle collision (unlikely with counter-based, but good practice)
            int attempts = 0;
            while (repository.existsByShortCode(shortCode) && attempts < 5) {
                shortCode = codeGenerator.generate();
                attempts++;
            }
            
            if (repository.existsByShortCode(shortCode)) {
                throw new RuntimeException("Failed to generate unique short code");
            }
        }
        
        // Create and save entity
        UrlEntity entity = new UrlEntityBuilder()
            .shortCode(shortCode)
            .longUrl(request.getLongUrl())
            .expiresAt(request.getExpiresAt())
            .userId(request.getUserId())
            .custom(isCustom)
            .build();
        
        repository.save(entity);
        
        return new CreateUrlResponse(
            shortCode,
            baseUrl,
            request.getLongUrl(),
            entity.getCreatedAt(),
            request.getExpiresAt()
        );
    }
    
    @Override
    public Optional<String> getOriginalUrl(String shortCode) {
        Optional<UrlEntity> entity = repository.findByShortCode(shortCode);
        
        if (entity.isEmpty()) {
            return Optional.empty();
        }
        
        UrlEntity url = entity.get();
        
        // Check expiration
        if (url.isExpired()) {
            throw new UrlExpiredException("URL has expired: " + shortCode);
        }
        
        // Increment click count (synchronous in v1)
        // In v2+: This would be async via message queue
        repository.incrementClickCount(shortCode);
        
        return Optional.of(url.getLongUrl());
    }
    
    @Override
    public Optional<UrlStats> getStats(String shortCode) {
        return repository.findByShortCode(shortCode)
            .map(entity -> new UrlStats(
                entity.getShortCode(),
                entity.getLongUrl(),
                entity.getClickCount(),
                entity.getCreatedAt(),
                entity.getExpiresAt()
            ));
    }
    
    @Override
    public boolean deleteUrl(String shortCode) {
        return repository.deleteByShortCode(shortCode);
    }
    
    /**
     * Validate URL format.
     */
    private void validateUrl(String urlString) {
        if (urlString == null || urlString.isEmpty()) {
            throw new IllegalArgumentException("URL cannot be empty");
        }
        
        try {
            URL url = new URL(urlString);
            String protocol = url.getProtocol().toLowerCase();
            
            if (!protocol.equals("http") && !protocol.equals("https")) {
                throw new IllegalArgumentException("Only HTTP/HTTPS URLs are allowed");
            }
        } catch (MalformedURLException e) {
            throw new IllegalArgumentException("Invalid URL format: " + urlString);
        }
    }
}

/**
 * Exception for duplicate custom aliases.
 */
class AliasAlreadyExistsException extends RuntimeException {
    public AliasAlreadyExistsException(String message) {
        super(message);
    }
}

/**
 * Exception for expired URLs.
 */
class UrlExpiredException extends RuntimeException {
    public UrlExpiredException(String message) {
        super(message);
    }
}

/**
 * Exception for URL not found.
 */
class UrlNotFoundException extends RuntimeException {
    public UrlNotFoundException(String message) {
        super(message);
    }
}
