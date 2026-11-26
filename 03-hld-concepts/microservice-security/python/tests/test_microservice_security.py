import unittest
import time
from src.microservice_security import MicroserviceSecurityService

class TestMicroserviceSecurity(unittest.TestCase):
    def test_pkce_challenge_verification(self):
        service = MicroserviceSecurityService()
        verifier = "my_secret_code_verifier_1234567890"
        challenge = service.generate_pkce_challenge(verifier)
        
        self.assertTrue(service.verify_pkce_challenge(verifier, challenge))
        self.assertFalse(service.verify_pkce_challenge("wrong_verifier", challenge))

    def test_valid_jwt_authorization(self):
        service = MicroserviceSecurityService("secret")
        token = service.build_jwt(
            subject="user123",
            issuer="auth-server",
            audience="my-api",
            roles=["user", "admin"]
        )
        
        payload = service.validate_jwt(token, "auth-server", "my-api")
        self.assertEqual(payload["sub"], "user123")
        self.assertIn("admin", payload["roles"])
        
        self.assertTrue(service.check_permission(token, "admin", "auth-server", "my-api"))
        self.assertFalse(service.check_permission(token, "superadmin", "auth-server", "my-api"))

    def test_expired_token_rejection(self):
        service = MicroserviceSecurityService("secret")
        # Expired token
        token = service.build_jwt(
            subject="user123",
            issuer="auth-server",
            audience="my-api",
            roles=["user"],
            expiration_seconds=-10 # expired 10 seconds ago
        )
        
        with self.assertRaisesRegex(ValueError, "JWT has expired"):
            service.validate_jwt(token, "auth-server", "my-api")

    def test_tampered_signature_rejection(self):
        service = MicroserviceSecurityService("secret")
        token = service.build_jwt(
            subject="user123",
            issuer="auth-server",
            audience="my-api",
            roles=["user"]
        )
        
        # Tamper with the token
        parts = token.split('.')
        parts[2] = parts[2][:-1] + ('A' if parts[2][-1] != 'A' else 'B')
        tampered_token = '.'.join(parts)
        
        with self.assertRaisesRegex(ValueError, "Invalid JWT signature"):
            service.validate_jwt(tampered_token, "auth-server", "my-api")

    def test_invalid_issuer_and_audience(self):
        service = MicroserviceSecurityService("secret")
        token = service.build_jwt(
            subject="user123",
            issuer="auth-server",
            audience="my-api",
            roles=["user"]
        )
        
        with self.assertRaisesRegex(ValueError, "Invalid issuer"):
            service.validate_jwt(token, "wrong-issuer", "my-api")
            
        with self.assertRaisesRegex(ValueError, "Invalid audience"):
            service.validate_jwt(token, "auth-server", "wrong-api")

if __name__ == '__main__':
    unittest.main()
