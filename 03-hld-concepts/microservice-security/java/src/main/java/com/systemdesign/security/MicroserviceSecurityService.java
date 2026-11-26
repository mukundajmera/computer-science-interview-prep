package com.systemdesign.security;

import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.util.Base64;
import java.util.List;
import javax.crypto.Mac;
import javax.crypto.spec.SecretKeySpec;
import java.util.regex.Pattern;

public class MicroserviceSecurityService {
    private final byte[] jwtSecret;

    public MicroserviceSecurityService(String jwtSecret) {
        this.jwtSecret = jwtSecret.getBytes(StandardCharsets.UTF_8);
    }

    public MicroserviceSecurityService() {
        this("super_secret_key");
    }

    public String generatePkceChallenge(String verifier) throws NoSuchAlgorithmException {
        MessageDigest digest = MessageDigest.getInstance("SHA-256");
        byte[] hash = digest.digest(verifier.getBytes(StandardCharsets.UTF_8));
        return Base64.getUrlEncoder().withoutPadding().encodeToString(hash);
    }

    public boolean verifyPkceChallenge(String verifier, String challenge) {
        try {
            String expectedChallenge = generatePkceChallenge(verifier);
            return MessageDigest.isEqual(expectedChallenge.getBytes(StandardCharsets.UTF_8), 
                                         challenge.getBytes(StandardCharsets.UTF_8));
        } catch (NoSuchAlgorithmException e) {
            throw new RuntimeException("SHA-256 not supported", e);
        }
    }

    private String base64UrlEncode(byte[] data) {
        return Base64.getUrlEncoder().withoutPadding().encodeToString(data);
    }

    public String buildJwt(String subject, String issuer, String audience, List<String> roles, int expirationSeconds) {
        try {
            String headerJson = "{\"alg\":\"HS256\",\"typ\":\"JWT\"}";
            long now = System.currentTimeMillis() / 1000;
            long exp = now + expirationSeconds;
            
            StringBuilder rolesJson = new StringBuilder("[");
            for (int i = 0; i < roles.size(); i++) {
                rolesJson.append("\"").append(roles.get(i)).append("\"");
                if (i < roles.size() - 1) {
                    rolesJson.append(",");
                }
            }
            rolesJson.append("]");

            String payloadJson = String.format(
                "{\"sub\":\"%s\",\"iss\":\"%s\",\"aud\":\"%s\",\"roles\":%s,\"iat\":%d,\"exp\":%d}",
                subject, issuer, audience, rolesJson.toString(), now, exp
            );

            String headerB64 = base64UrlEncode(headerJson.getBytes(StandardCharsets.UTF_8));
            String payloadB64 = base64UrlEncode(payloadJson.getBytes(StandardCharsets.UTF_8));
            
            String unsignedToken = headerB64 + "." + payloadB64;
            
            Mac mac = Mac.getInstance("HmacSHA256");
            SecretKeySpec secretKey = new SecretKeySpec(jwtSecret, "HmacSHA256");
            mac.init(secretKey);
            
            byte[] signature = mac.doFinal(unsignedToken.getBytes(StandardCharsets.UTF_8));
            String signatureB64 = base64UrlEncode(signature);
            
            return unsignedToken + "." + signatureB64;
        } catch (Exception e) {
            throw new RuntimeException("Error building JWT", e);
        }
    }

    public String validateJwt(String token, String expectedIssuer, String expectedAudience) {
        try {
            String[] parts = token.split("\\.");
            if (parts.length != 3) {
                throw new IllegalArgumentException("Invalid JWT format.");
            }

            String headerB64 = parts[0];
            String payloadB64 = parts[1];
            String signatureB64 = parts[2];

            String unsignedToken = headerB64 + "." + payloadB64;
            
            Mac mac = Mac.getInstance("HmacSHA256");
            SecretKeySpec secretKey = new SecretKeySpec(jwtSecret, "HmacSHA256");
            mac.init(secretKey);
            
            byte[] expectedSignature = mac.doFinal(unsignedToken.getBytes(StandardCharsets.UTF_8));
            String expectedSignatureB64 = base64UrlEncode(expectedSignature);
            
            if (!MessageDigest.isEqual(signatureB64.getBytes(StandardCharsets.UTF_8), 
                                       expectedSignatureB64.getBytes(StandardCharsets.UTF_8))) {
                throw new IllegalArgumentException("Invalid JWT signature.");
            }

            // Manually pad base64url if needed for standard decoder
            String paddedPayloadB64 = payloadB64;
            while (paddedPayloadB64.length() % 4 != 0) {
                paddedPayloadB64 += "=";
            }
            paddedPayloadB64 = paddedPayloadB64.replace('-', '+').replace('_', '/');
            
            byte[] payloadBytes = Base64.getDecoder().decode(paddedPayloadB64);
            String payloadJson = new String(payloadBytes, StandardCharsets.UTF_8);

            // Simple parsing to avoid pulling in external JSON library dependencies
            long now = System.currentTimeMillis() / 1000;
            
            // Check exp
            java.util.regex.Matcher expMatcher = Pattern.compile("\"exp\":(\\d+)").matcher(payloadJson);
            if (expMatcher.find()) {
                long exp = Long.parseLong(expMatcher.group(1));
                if (exp < now) {
                    throw new IllegalArgumentException("JWT has expired.");
                }
            }

            // Check iss
            java.util.regex.Matcher issMatcher = Pattern.compile("\"iss\":\"([^\"]+)\"").matcher(payloadJson);
            if (issMatcher.find()) {
                String iss = issMatcher.group(1);
                if (!expectedIssuer.equals(iss)) {
                    throw new IllegalArgumentException("Invalid issuer. Expected " + expectedIssuer + ".");
                }
            } else {
                 throw new IllegalArgumentException("Invalid issuer. Expected " + expectedIssuer + ".");
            }

            // Check aud
            java.util.regex.Matcher audMatcher = Pattern.compile("\"aud\":\"([^\"]+)\"").matcher(payloadJson);
            if (audMatcher.find()) {
                String aud = audMatcher.group(1);
                if (!expectedAudience.equals(aud)) {
                    throw new IllegalArgumentException("Invalid audience. Expected " + expectedAudience + ".");
                }
            } else {
                 throw new IllegalArgumentException("Invalid audience. Expected " + expectedAudience + ".");
            }

            return payloadJson;
        } catch (IllegalArgumentException e) {
            throw e;
        } catch (Exception e) {
            throw new RuntimeException("Error validating JWT", e);
        }
    }

    public boolean checkPermission(String token, String requiredRole, String expectedIssuer, String expectedAudience) {
        String payloadJson = validateJwt(token, expectedIssuer, expectedAudience);
        // Look for the exact role in the JSON roles array string (simple check for stdlib only)
        return payloadJson.contains("\"" + requiredRole + "\"");
    }
}
