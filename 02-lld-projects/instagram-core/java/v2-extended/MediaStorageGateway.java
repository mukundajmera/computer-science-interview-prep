import java.util.UUID;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;

public class MediaStorageGateway {
    private final Map<String, String> storage = new ConcurrentHashMap<>();

    public String put(String mediaBytesRef) {
        String mediaKey = UUID.randomUUID().toString();
        storage.put(mediaKey, mediaBytesRef);
        return mediaKey;
    }

    public String get(String mediaKey) {
        return storage.get(mediaKey);
    }
}
