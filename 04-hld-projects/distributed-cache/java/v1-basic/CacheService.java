package dcache.v1;

import java.util.Optional;

public interface CacheService {
    void set(String key, String value, long ttlSeconds);
    Optional<String> get(String key);
    boolean delete(String key);
}
