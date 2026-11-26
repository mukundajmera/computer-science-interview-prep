package com.systemdesign.security;

import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.BeforeEach;

import java.util.Arrays;
import java.util.List;

import static org.junit.jupiter.api.Assertions.*;

public class MicroserviceSecurityServiceTest {

    private MicroserviceSecurityService service;

    @BeforeEach
    public void setup() {
        service = new MicroserviceSecurityService("secret_test_key");
    }

    @Test
    public void testPkceChallengeVerification() throws Exception {
        String verifier = "my_secret_code_verifier_1234567890";
        String challenge = service.generatePkceChallenge(verifier);
        
        assertTrue(service.verifyPkceChallenge(verifier, challenge));
        assertFalse(service.verifyPkceChallenge("wrong_verifier", challenge));
    }

    @Test
    public void testValidJwtAuthorization() {
        List<String> roles = Arrays.asList("user", "admin");
        String token = service.buildJwt("user123", "auth-server", "my-api", roles, 3600);
        
        String payload = service.validateJwt(token, "auth-server", "my-api");
        assertTrue(payload.contains("\"sub\":\"user123\""));
        
        assertTrue(service.checkPermission(token, "admin", "auth-server", "my-api"));
        assertFalse(service.checkPermission(token, "superadmin", "auth-server", "my-api"));
    }

    @Test
    public void testExpiredTokenRejection() {
        List<String> roles = Arrays.asList("user");
        // Token expired 10 seconds ago
        String token = service.buildJwt("user123", "auth-server", "my-api", roles, -10);
        
        Exception exception = assertThrows(IllegalArgumentException.class, () -> {
            service.validateJwt(token, "auth-server", "my-api");
        });
        
        assertEquals("JWT has expired.", exception.getMessage());
    }

    @Test
    public void testTamperedSignatureRejection() {
        List<String> roles = Arrays.asList("user");
        String token = service.buildJwt("user123", "auth-server", "my-api", roles, 3600);
        
        String[] parts = token.split("\\.");
        // Tamper with signature
        String tamperedSignature = parts[2].substring(0, parts[2].length() - 1) + 
                                   (parts[2].endsWith("A") ? "B" : "A");
        String tamperedToken = parts[0] + "." + parts[1] + "." + tamperedSignature;
        
        Exception exception = assertThrows(IllegalArgumentException.class, () -> {
            service.validateJwt(tamperedToken, "auth-server", "my-api");
        });
        
        assertEquals("Invalid JWT signature.", exception.getMessage());
    }

    @Test
    public void testInvalidIssuerAndAudience() {
        List<String> roles = Arrays.asList("user");
        String token = service.buildJwt("user123", "auth-server", "my-api", roles, 3600);
        
        Exception exception1 = assertThrows(IllegalArgumentException.class, () -> {
            service.validateJwt(token, "wrong-issuer", "my-api");
        });
        assertEquals("Invalid issuer. Expected wrong-issuer.", exception1.getMessage());
        
        Exception exception2 = assertThrows(IllegalArgumentException.class, () -> {
            service.validateJwt(token, "auth-server", "wrong-api");
        });
        assertEquals("Invalid audience. Expected wrong-api.", exception2.getMessage());
    }
}
