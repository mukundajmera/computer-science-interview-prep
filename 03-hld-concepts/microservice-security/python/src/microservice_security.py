import base64
import hashlib
import hmac
import json
import time
import secrets
from typing import Dict, Any, List

class MicroserviceSecurityService:
    def __init__(self, jwt_secret: str = "super_secret_key"):
        self.jwt_secret = jwt_secret.encode('utf-8')
        
    def generate_pkce_challenge(self, verifier: str) -> str:
        """
        Generates a PKCE code challenge from a verifier using SHA-256 and base64url encoding.
        """
        digest = hashlib.sha256(verifier.encode('utf-8')).digest()
        # base64url encode without padding
        return base64.urlsafe_b64encode(digest).decode('utf-8').rstrip('=')

    def verify_pkce_challenge(self, verifier: str, challenge: str) -> bool:
        """
        Verifies if a code verifier matches the given challenge.
        """
        expected_challenge = self.generate_pkce_challenge(verifier)
        return hmac.compare_digest(expected_challenge, challenge)

    def _base64url_encode(self, data: bytes) -> str:
        return base64.urlsafe_b64encode(data).decode('utf-8').rstrip('=')

    def build_jwt(self, subject: str, issuer: str, audience: str, roles: List[str], expiration_seconds: int = 3600) -> str:
        """
        Builds a signed JWT (HS256) with standard claims.
        """
        header = {"alg": "HS256", "typ": "JWT"}
        now = int(time.time())
        payload = {
            "sub": subject,
            "iss": issuer,
            "aud": audience,
            "roles": roles,
            "iat": now,
            "exp": now + expiration_seconds
        }
        
        header_b64 = self._base64url_encode(json.dumps(header).encode('utf-8'))
        payload_b64 = self._base64url_encode(json.dumps(payload).encode('utf-8'))
        
        unsigned_token = f"{header_b64}.{payload_b64}"
        signature = hmac.new(self.jwt_secret, unsigned_token.encode('utf-8'), hashlib.sha256).digest()
        signature_b64 = self._base64url_encode(signature)
        
        return f"{unsigned_token}.{signature_b64}"

    def validate_jwt(self, token: str, expected_issuer: str, expected_audience: str) -> Dict[str, Any]:
        """
        Validates JWT signature, expiration, issuer, and audience.
        Returns payload if valid, otherwise raises ValueError.
        """
        parts = token.split('.')
        if len(parts) != 3:
            raise ValueError("Invalid JWT format.")
            
        header_b64, payload_b64, signature_b64 = parts
        
        # Verify signature
        unsigned_token = f"{header_b64}.{payload_b64}"
        expected_signature = hmac.new(self.jwt_secret, unsigned_token.encode('utf-8'), hashlib.sha256).digest()
        expected_signature_b64 = self._base64url_encode(expected_signature)
        
        if not hmac.compare_digest(signature_b64, expected_signature_b64):
            raise ValueError("Invalid JWT signature.")
            
        # Parse payload
        # Add padding back if necessary
        payload_padded = payload_b64 + '=' * (-len(payload_b64) % 4)
        payload_json = base64.urlsafe_b64decode(payload_padded).decode('utf-8')
        payload = json.loads(payload_json)
        
        # Validate claims
        now = int(time.time())
        if "exp" in payload and payload["exp"] < now:
            raise ValueError("JWT has expired.")
            
        if payload.get("iss") != expected_issuer:
            raise ValueError(f"Invalid issuer. Expected {expected_issuer}.")
            
        if payload.get("aud") != expected_audience:
            raise ValueError(f"Invalid audience. Expected {expected_audience}.")
            
        return payload

    def check_permission(self, token: str, required_role: str, expected_issuer: str, expected_audience: str) -> bool:
        """
        Validates token and checks if user has the required role.
        """
        payload = self.validate_jwt(token, expected_issuer, expected_audience)
        roles = payload.get("roles", [])
        return required_role in roles
