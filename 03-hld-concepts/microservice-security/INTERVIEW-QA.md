# Microservice Security & Zero Trust - Interview Q&A

## 1. How do you handle token revocation efficiently at scale without introducing a central point of failure?
**Answer:**
Revocation is challenging in a stateless JWT architecture. Strategies include:
1. **Short Expirations:** Issue access tokens valid for 5-15 minutes. Revoking the refresh token limits the attack window.
2. **Denylist (Blacklist):** Maintain a distributed cache (e.g., Redis) of revoked JWT signatures or `jti` (JWT ID). API Gateways/Sidecars check this cache. Since it only stores revoked tokens that haven't expired yet, the data size is small.
3. **Bloom Filters:** Propagate a Bloom filter of revoked `jti`s to sidecars. It's memory efficient. If a hit occurs (potential false positive), the sidecar falls back to a precise check against a central database.

## 2. What is the performance overhead of using an Envoy sidecar for mTLS and JWT verification, and how do you optimize it?
**Answer:**
**Overhead:** Envoy adds latency for local network hops (loopback), CPU overhead for cryptographic operations (TLS handshakes, JWT signature verification), and memory footprint per sidecar.
**Optimization:**
- **Connection Pooling & Keep-Alive:** Reuse mTLS connections between sidecars to avoid frequent TLS handshakes.
- **JWKS Caching:** The sidecar caches the public keys from the JWKS endpoint, performing JWT validation entirely locally in memory.
- **Hardware Acceleration:** Offloading cryptographic operations (like AES-GCM for TLS) to CPU hardware instructions (AES-NI).
- **Ext_authz Caching:** If external authorization policies are complex, cache the decisions locally for a short duration.

## 3. Explain how SPIRE manages to rotate mTLS certificates across thousands of nodes without causing service disruption.
**Answer:**
SPIRE uses a short-lived SVID (SPIFFE Verifiable Identity Document) strategy. 
1. The SPIRE Agent runs on each node and maintains a secure connection to the SPIRE Server.
2. When a workload's certificate is nearing its expiration (e.g., half its lifetime), the Agent preemptively requests a new certificate from the Server.
3. The Agent securely pushes the new certificate and private key to the workload via the Envoy SDS (Secret Discovery Service) API.
4. Envoy dynamically reloads the new certificate into its memory *without* dropping existing connections or requiring a restart.

## 4. How does the Authorization Code flow with PKCE prevent the Authorization Code Interception attack?
**Answer:**
In mobile or single-page apps (where client secrets can't be securely stored), a malicious app might intercept the Authorization Code via a custom OS URI scheme.
PKCE solves this:
1. The client generates a random `code_verifier` and sends its hashed version (`code_challenge`) to the auth server when requesting the code.
2. Even if a malicious app intercepts the resulting Authorization Code, it cannot exchange it for an Access Token because the final token exchange requires the *original, unhashed* `code_verifier`.
3. The malicious app does not know the `code_verifier`, so the auth server rejects the request.

## 5. In a service mesh, should the API Gateway or the Sidecar perform JWT validation?
**Answer:**
Both, adhering to Defense in Depth (Zero Trust):
- **API Gateway (Edge):** Validates the JWT from the external user (verifying signature, expiration, issuer) and translates it if necessary. This rejects unauthenticated traffic early, saving internal resources.
- **Envoy Sidecar (Local):** Performs local JWT verification again (trusting nothing) and checks fine-grained permissions or scopes specific to that microservice. It also enforces mTLS identity for the incoming connection from the Gateway or other internal services.

## 6. How do you design authorization (RBAC vs ABAC) in a highly distributed microservice architecture?
**Answer:**
- **RBAC (Role-Based Access Control):** Good for coarse-grained permissions (e.g., `admin`, `viewer`). Scopes or roles can be embedded directly in the JWT payload. Sidecars can parse the JWT and enforce RBAC policies locally (e.g., using OPA - Open Policy Agent).
- **ABAC (Attribute-Based Access Control):** Fine-grained (e.g., "User can edit document X if they created it"). This usually requires contextual data not present in the JWT. Solutions involve sidecars calling out to a centralized policy engine (OPA) providing the request context, and the engine querying a specialized data store (like Google Zanzibar) for relationship evaluation.

## 7. What is the "Confused Deputy" problem in microservices, and how do you mitigate it?
**Answer:**
**Problem:** Service A calls Service B. Service B has high privileges and is tricked into performing a malicious action on behalf of Service A, using B's privileges instead of A's.
**Mitigation:**
1. **Audience (`aud`) Restriction:** Ensure tokens are minted for a specific audience. Service B should reject a token intended for Service C.
2. **Token Exchange (RFC 8693):** Service A passes its token to Service B. Service B uses an STS (Security Token Service) to exchange the user's token for a new token scoped specifically for calling downstream services, maintaining the original user context but limiting the scope.

## 8. Why is the `alg: "none"` vulnerability dangerous, and how do you secure JWT validation against it?
**Answer:**
**Vulnerability:** If an attacker modifies a JWT payload, removes the signature, and sets the header to `{"alg": "none"}`, a poorly configured validation library might accept the token as valid because it sees "no signature required."
**Mitigation:** 
Never dynamically trust the `alg` specified in the JWT header for selecting the verification strategy. The resource server must hardcode the expected algorithm (e.g., `algorithms=["RS256"]`) and the corresponding public key when configuring the JWT validation library.

## 9. How do you manage Machine-to-Machine (M2M) authentication securely?
**Answer:**
Use the **OAuth 2.0 Client Credentials flow**.
1. Microservice A is issued a `client_id` and securely stores a `client_secret` (e.g., via HashiCorp Vault or Kubernetes Secrets).
2. Service A calls the Authorization Server, authenticates with its credentials, and receives an Access Token.
3. Service A uses this token as a Bearer token in the `Authorization` header to call Service B.
Alternatively, use **mTLS with SPIFFE/SPIRE**, where identity is cryptographically proven via TLS certificates, bypassing the need for token exchanges entirely for internal M2M.

## 10. Contrast asymmetric (RS256) vs symmetric (HS256) JWT signatures in a microservice ecosystem.
**Answer:**
- **Symmetric (HS256):** The Authorization Server and every microservice must share the exact same secret key. If any microservice is compromised, the secret is leaked, and the attacker can forge valid tokens for the entire system.
- **Asymmetric (RS256):** The Authorization Server signs the JWT with its Private Key. Microservices verify the token using the Public Key (fetched via JWKS). If a microservice is compromised, only the public key is leaked, which cannot be used to forge tokens. Asymmetric is mandatory for scalable microservice security.
