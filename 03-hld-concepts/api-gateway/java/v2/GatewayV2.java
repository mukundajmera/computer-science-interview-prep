import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import javax.crypto.Mac;
import javax.crypto.spec.SecretKeySpec;
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;

interface Filter {
    String execute(Map<String, String> request);
}

class AuthFilter implements Filter {
    private final String secretKey;

    public AuthFilter(String secretKey) {
        this.secretKey = secretKey;
    }

    private static String bytesToHex(byte[] hash) {
        StringBuilder hexString = new StringBuilder(2 * hash.length);
        for (int i = 0; i < hash.length; i++) {
            String hex = Integer.toHexString(0xff & hash[i]);
            if(hex.length() == 1) {
                hexString.append('0');
            }
            hexString.append(hex);
        }
        return hexString.toString();
    }

    @Override
    public String execute(Map<String, String> request) {
        String token = request.get("token");
        if (token == null) return "401 Unauthorized";

        String[] parts = token.split("\\.");
        if (parts.length != 2) return "401 Unauthorized";

        String payload = parts[0];
        String signature = parts[1];

        try {
            Mac sha256_HMAC = Mac.getInstance("HmacSHA256");
            SecretKeySpec secret_key = new SecretKeySpec(secretKey.getBytes(StandardCharsets.UTF_8), "HmacSHA256");
            sha256_HMAC.init(secret_key);

            byte[] hash = sha256_HMAC.doFinal(payload.getBytes(StandardCharsets.UTF_8));
            String expectedSig = bytesToHex(hash);

            if (!MessageDigest.isEqual(expectedSig.getBytes(StandardCharsets.UTF_8), signature.getBytes(StandardCharsets.UTF_8))) {
                return "401 Unauthorized";
            }
        } catch (Exception e) {
            return "401 Unauthorized";
        }
        
        return null; // success
    }
}

class RateLimitFilter implements Filter {
    private final int capacity;
    private final double refillRate;
    private double tokens;
    private long lastRefill;

    public RateLimitFilter(int capacity, double refillRate) {
        this.capacity = capacity;
        this.refillRate = refillRate;
        this.tokens = capacity;
        this.lastRefill = System.currentTimeMillis();
    }

    @Override
    public String execute(Map<String, String> request) {
        long now = System.currentTimeMillis();
        double timePassedSec = (now - lastRefill) / 1000.0;
        
        tokens = Math.min(capacity, tokens + timePassedSec * refillRate);
        lastRefill = now;

        if (tokens >= 1.0) {
            tokens -= 1.0;
            return null; // success
        }
        
        return "429 Too Many Requests";
    }
}

public class GatewayV2 {
    private final List<Filter> filters = new ArrayList<>();

    public void addFilter(Filter filter) {
        filters.add(filter);
    }

    public String handle(Map<String, String> request) {
        for (Filter f : filters) {
            String err = f.execute(request);
            if (err != null) {
                return err;
            }
        }
        return "200 OK -> " + request.get("path");
    }
}
