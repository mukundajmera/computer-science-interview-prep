import java.util.HashMap;
import java.util.Map;
import javax.crypto.Mac;
import javax.crypto.spec.SecretKeySpec;
import java.nio.charset.StandardCharsets;

public class GatewayV2Test {

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

    private static String generateToken(String payload, String secretKey) throws Exception {
        Mac sha256_HMAC = Mac.getInstance("HmacSHA256");
        SecretKeySpec secret_key = new SecretKeySpec(secretKey.getBytes(StandardCharsets.UTF_8), "HmacSHA256");
        sha256_HMAC.init(secret_key);

        byte[] hash = sha256_HMAC.doFinal(payload.getBytes(StandardCharsets.UTF_8));
        String signature = bytesToHex(hash);
        return payload + "." + signature;
    }

    public static void main(String[] args) throws Exception {
        testMissingToken();
        testInvalidToken();
        testValidToken();
        testRateLimiting();
        System.out.println("GatewayV2Test passed.");
    }

    private static void testMissingToken() {
        GatewayV2 gateway = new GatewayV2();
        gateway.addFilter(new AuthFilter("secret"));

        Map<String, String> req = new HashMap<>();
        req.put("path", "/api");

        assert "401 Unauthorized".equals(gateway.handle(req)) : "Expected 401";
    }

    private static void testInvalidToken() {
        GatewayV2 gateway = new GatewayV2();
        gateway.addFilter(new AuthFilter("secret"));

        Map<String, String> req = new HashMap<>();
        req.put("path", "/api");
        req.put("token", "user1.bad_sig");

        assert "401 Unauthorized".equals(gateway.handle(req)) : "Expected 401";
    }

    private static void testValidToken() throws Exception {
        GatewayV2 gateway = new GatewayV2();
        gateway.addFilter(new AuthFilter("secret"));

        Map<String, String> req = new HashMap<>();
        req.put("path", "/api");
        req.put("token", generateToken("user1", "secret"));

        assert "200 OK -> /api".equals(gateway.handle(req)) : "Expected 200";
    }

    private static void testRateLimiting() throws Exception {
        GatewayV2 gateway = new GatewayV2();
        gateway.addFilter(new AuthFilter("secret"));
        gateway.addFilter(new RateLimitFilter(2, 0.0)); // 2 capacity, no refill

        Map<String, String> req = new HashMap<>();
        req.put("path", "/api");
        req.put("token", generateToken("user1", "secret"));

        assert "200 OK -> /api".equals(gateway.handle(req)) : "Expected 200 on req 1";
        assert "200 OK -> /api".equals(gateway.handle(req)) : "Expected 200 on req 2";
        assert "429 Too Many Requests".equals(gateway.handle(req)) : "Expected 429 on req 3";
    }
}
