# Security & Auth Answers

## Question 1

1. **A** - Authorization Code Grant

**Explanation:** The Authorization Code Grant is the standard and most secure flow for web applications. It involves the client redirecting the user to the authorization server, which then redirects back with an authorization code. The client's backend securely exchanges this code (along with a client secret) for an access token via a direct, backend-to-backend API call. This ensures the access token is never exposed to the user's browser, unlike the Implicit Grant (which is now deprecated for security reasons).

## Question 2

2. **C** - To provide authentication and identity verification, resulting in an ID Token.

**Explanation:** OAuth 2.0 is an *authorization* framework; it delegates access (via access tokens) but does not technically authenticate the user or provide identity information to the client. OpenID Connect (OIDC) is an identity layer built on top of OAuth 2.0. It standardizes the authentication process and introduces the 'ID Token' (usually a JWT), which contains verified information about the user's identity (like name and email).

## Question 3

3. **D** - Header, Payload, and Signature.

**Explanation:** A JSON Web Token (JWT) is a standard for securely transmitting information as a JSON object. It consists of three parts separated by dots ('.'): 1) The Header (specifies the token type and signing algorithm), 2) The Payload (contains the claims, which are statements about the user and other metadata), and 3) The Signature (created using the encoded header, encoded payload, a secret, and the specified algorithm to verify the token hasn't been altered).

## Question 4

4. **C** - By using the pre-shared secret or the authorization server's public key to cryptographically validate the JWT's signature.

**Explanation:** The power of JWTs is that they are stateless. Because the token contains a cryptographic signature, the resource server can verify its authenticity and integrity independently. If the token was signed with a symmetric algorithm (like HS256), the server needs the shared secret. If it was signed with an asymmetric algorithm (like RS256), the server can fetch the authorization server's public key (e.g., from a JWKS endpoint) to verify the signature locally.

## Question 5

5. **C** - Symmetric encryption uses the same key for both encryption and decryption, while asymmetric encryption uses a public key to encrypt and a private key to decrypt.

**Explanation:** Symmetric encryption relies on a single shared secret key for both encrypting and decrypting data (e.g., AES). It is very fast. Asymmetric encryption uses a mathematically linked key pair: a public key (which can be shared openly) to encrypt data, and a private key (which must be kept secret) to decrypt it (e.g., RSA, ECC). Asymmetric encryption solves the problem of securely sharing keys but is computationally much slower, so it is often used just to establish a session key for symmetric encryption.

## Question 6

6. **A** - It requires both the client and the server to authenticate each other using cryptographic certificates.

**Explanation:** In standard TLS (HTTPS), only the server presents a certificate to prove its identity to the client; the client remains anonymous to the transport layer. In Mutual TLS (mTLS), both parties authenticate each other. The server verifies the client's certificate, and the client verifies the server's certificate. This provides strong, cryptographic, machine-to-machine authentication, making it a critical component of Zero Trust architectures.

## Question 7

7. **C** - Cross-Site Request Forgery (CSRF)

**Explanation:** Cross-Site Request Forgery (CSRF) exploits the fact that browsers automatically include session cookies with cross-origin requests. An attacker can create a malicious website containing a hidden request (e.g., a form submission to a banking site). If the victim visits the malicious site while logged into their bank, the browser will send the request to the bank, attaching the victim's session cookies, and the bank will execute the action (like transferring money) assuming the user intended it.

## Question 8

8. **C** - Context-aware output encoding/escaping and implementing a strong Content Security Policy (CSP).

**Explanation:** Cross-Site Scripting (XSS) occurs when an application includes untrusted data in a web page without proper validation or escaping, allowing the attacker to execute malicious scripts in the victim's browser. The primary defense is context-aware output encoding: ensuring any user input reflected on the page is treated as data, not executable code (e.g., converting `<` to `&lt;`). Additionally, a Content Security Policy (CSP) restricts where scripts can be loaded from and prevents inline script execution.

## Question 9

9. **D** - The server generates a unique, unpredictable token that the client must include in the body or header of every state-changing request, which attackers cannot predict or read.

**Explanation:** To prevent CSRF, the server issues a cryptographically strong, random token and embeds it in the HTML (or sends it via a header/cookie read by JS). When the client submits a form or API request, it must include this token. Because the attacker's malicious site cannot read data from the target site (due to the Same-Origin Policy), the attacker cannot obtain the token to include in their forged request. The server rejects requests missing the correct token.

## Question 10

10. **D** - To allow the client application to obtain a new access token without requiring the user to re-authenticate, after the current access token expires.

**Explanation:** Access tokens typically have short lifespans (e.g., 15 minutes to 1 hour) to limit the window of opportunity if they are stolen. To maintain a long-lived session without constantly prompting the user to log in again, the authorization server can issue a Refresh Token. This token is stored securely by the client and sent to the authorization server to request a fresh access token. Refresh tokens are long-lived and can be independently revoked by the server.

## Question 11

11. **B** - It returns the access token directly in the URL fragment (hash), exposing it to browser history, logs, and potential XSS attacks.

**Explanation:** The Implicit flow was originally designed for SPAs because they couldn't securely store a client secret. In this flow, the authorization server redirects back to the SPA with the access token appended to the URL fragment (e.g., `#access_token=...`). This is highly insecure because the token can be leaked via browser history, proxy logs, or easily stolen if the SPA suffers from an XSS vulnerability. The modern recommendation is to use the Authorization Code flow with PKCE.

## Question 12

12. **B** - An extension to the Authorization Code flow that prevents authorization code interception attacks, especially in public clients like mobile apps and SPAs.

**Explanation:** Public clients (like mobile apps and SPAs) cannot securely store a Client Secret, meaning anyone could potentially intercept an authorization code and exchange it for a token. PKCE solves this by generating a dynamic, temporary secret (the 'code verifier') and its hash (the 'code challenge') for every authorization request. The authorization server only issues the token if the client can provide the original 'code verifier' during the token exchange step.

## Question 13

13. **A** - A user, process, or system should only be given the bare minimum permissions necessary to perform its intended function.

**Explanation:** The Principle of Least Privilege (PoLP) is a fundamental security concept. It dictates that entities (users, services, applications) should only have the access rights necessary to complete their specific tasks, and nothing more. This minimizes the attack surface and limits the potential blast radius if an entity is compromised.

## Question 14

14. **C** - It prevents client-side scripts (like JavaScript) from accessing the cookie, mitigating the risk of cookie theft via XSS attacks.

**Explanation:** When a cookie is marked as `HttpOnly`, the browser forbids any client-side scripts (e.g., `document.cookie` in JavaScript) from accessing it. If an application suffers from an XSS vulnerability, the attacker's malicious script will not be able to read and steal the `HttpOnly` cookie (which often contains the session ID or access token). The 'Secure' flag enforces HTTPS, and the 'SameSite' attribute mitigates CSRF.

## Question 15

15. **D** - Maintaining a centralized 'denylist' (or blocklist) of revoked token signatures or IDs (jti) that the resource server must check, often stored in a fast cache like Redis.

**Explanation:** Because JWTs are validated locally by the resource server, revoking them before they expire is challenging. A common solution is to maintain a 'denylist' (blocklist) of revoked token IDs (the 'jti' claim). When a user logs out or is banned, their token ID is added to the denylist. The resource server must check this denylist (typically stored in a fast, distributed cache like Redis) for every request, which introduces a stateful check into a stateless system.

## Question 16

16. **A** - It instructs the browser to never send the cookie with cross-site requests, providing robust protection against CSRF attacks.

**Explanation:** The `SameSite` attribute controls how cookies are sent with cross-site requests. `SameSite=Strict` ensures the cookie is only sent in a first-party context (when the request originates from the same site that set the cookie). It will not be sent if the user follows a link from an external site or if an external site attempts to submit a form. This is a highly effective defense against Cross-Site Request Forgery (CSRF).

## Question 17

17. **A** - To digitally sign a server's public key, asserting that the key belongs to the legitimate owner of the domain name.

**Explanation:** A Certificate Authority (CA) acts as a trusted third party in PKI. When a server wants to enable HTTPS, it generates a key pair and sends a Certificate Signing Request (CSR) containing its public key and domain name to a CA. The CA verifies the organization's control over the domain. If verified, the CA digitally signs the server's public key using the CA's own private key, creating a digital certificate. Browsers trust the CA, so they trust the certificate.

## Question 18

18. **D** - A random string of data appended to a password before hashing, used to ensure identical passwords have unique hashes and to defend against rainbow table attacks.

**Explanation:** Hashing is a one-way function. If you hash 'password123', it always produces the same output. Attackers pre-compute hashes for millions of common passwords (creating 'rainbow tables'). A salt is a unique, random string generated for each user and added to their password before hashing. This ensures that even if two users have the same password, their hashes are completely different, rendering rainbow tables useless.

## Question 19

19. **B** - A vulnerability where an attacker tricks a server into making HTTP requests to internal or external systems on their behalf, often bypassing firewalls.

**Explanation:** SSRF occurs when a web application takes a URL as input from the user and fetches it from the backend server without proper validation. Attackers can provide URLs pointing to internal systems (e.g., `http://169.254.169.254` for AWS metadata, or `http://localhost:6379` for an internal Redis instance). The vulnerable server, operating behind the firewall, executes the request, allowing the attacker to interact with internal infrastructure.

## Question 20

20. **A** - Authentication verifies the identity of a user (who they are), while Authorization determines what permissions the user has (what they can do).

**Explanation:** Authentication (AuthN) is the process of proving you are who you say you are (e.g., logging in with a username/password or biometric). Authorization (AuthZ) occurs after authentication and determines what resources or actions you are permitted to access or perform based on your identity and roles (e.g., a standard user cannot access the admin panel). OpenID Connect is for AuthN, while OAuth 2.0 is for AuthZ.

## Question 21

21. **D** - Digital Signatures created using Asymmetric Encryption.

**Explanation:** Non-repudiation ensures that a sender cannot deny having sent a message. This is achieved using Digital Signatures, which rely on asymmetric encryption. The sender hashes the message and encrypts the hash with their *private key*. Anyone can use the sender's *public key* to decrypt the signature and verify the hash. Because only the sender possesses the private key, they cannot repudiate (deny) having signed it.

## Question 22

22. **B** - An attack that uses a massive pre-computed database of plaintext passwords and their corresponding hashes to quickly reverse hashed passwords.

**Explanation:** A rainbow table is a pre-computed dictionary of plaintext passwords and the hashes they generate. Instead of taking the time to hash guessed passwords during an attack (brute-forcing), the attacker simply looks up the stolen hash in the table to instantly find the corresponding plaintext. Adding a unique, random 'salt' to each password before hashing effectively defeats rainbow table attacks.

## Question 23

23. **A** - Passing a signed JWT (JSON Web Token) in the 'Authorization' header of every service-to-service HTTP request.

**Explanation:** In microservices, checking authorization at every hop by calling a central Auth service is inefficient and creates a bottleneck. Instead, the API Gateway or Edge proxy authenticates the user, generates (or validates) a JWT containing the user's identity and roles, and passes this JWT downstream in the HTTP headers. Because the JWT is cryptographically signed, downstream services can independently verify the token and extract the necessary authorization context without calling the Auth service.

## Question 24

24. **B** - It identifies the specific recipients (or resource servers) that the JWT is intended for, preventing a token issued for one API from being used against a completely different API.

**Explanation:** The `aud` (Audience) claim is a critical security control. It specifies the intended recipient of the token (e.g., `api.mycompany.com`). When a resource server receives a JWT, it must check the `aud` claim. If the claim does not match the server's own identifier, the server must reject the token. This prevents an attacker who obtained a token intended for a low-privilege API from using it to access a high-privilege API.

## Question 25

25. **B** - A WAF operates at Layer 7 (Application Layer) to analyze HTTP traffic for web-specific attacks like SQL injection and XSS, whereas a Network Firewall operates at Layers 3/4 to block IP addresses and ports.

**Explanation:** Traditional Network Firewalls operate at the Network and Transport layers (OSI Layers 3 and 4), allowing or blocking traffic based on IP addresses, protocols, and port numbers. A Web Application Firewall (WAF) operates at the Application Layer (Layer 7). It deeply inspects the content of HTTP/HTTPS requests and responses to detect and block complex web application attacks, such as SQL Injection (SQLi), Cross-Site Scripting (XSS), and Layer 7 DDoS attacks.

## Question 26

26. **A** - An attacker can change the algorithm to 'none', allowing them to forge tokens without needing the secret key, granting unauthorized access.

**Explanation:** The 'alg' header in a JWT specifies the cryptographic algorithm used to sign the token (e.g., HS256, RS256). A classic vulnerability occurs when a server blindly trusts this header without validation. An attacker can create a token, set the 'alg' header to 'none', and omit the signature entirely. If the server accepts this, it processes the token as valid, allowing the attacker to forge any claims (like changing their user ID or role) without needing the server's secret key, leading to complete system compromise.


## Question 27

27. **C** - To relax the browser's Same-Origin Policy in a controlled manner, allowing a web application running at one origin to access restricted resources from a different origin.

**Explanation:** By default, web browsers enforce the Same-Origin Policy (SOP), which prevents scripts on one origin from making requests to a different origin. CORS is a mechanism using additional HTTP headers that allows a server to explicitly declare which origins are permitted to read its resources, safely bypassing the SOP for authorized cross-origin requests.


## Question 28

28. **C** - Requiring a synchronized, cryptographically strong random anti-CSRF token in every state-changing request (e.g., POST, PUT, DELETE).

**Explanation:** Cross-Site Request Forgery (CSRF) occurs when a malicious site tricks a user's browser into making an unwanted request to a trusted site where the user is authenticated. Since browsers automatically include cookies (like session IDs) in these cross-origin requests, relying solely on cookies (even HttpOnly ones) does not prevent CSRF. The standard defense is the Synchronizer Token Pattern, which requires state-changing requests to include a unique, unpredictable anti-CSRF token (typically in a hidden form field or a custom HTTP header) that the attacker cannot easily guess or read, ensuring the request was intentionally initiated from the legitimate application.


## Question 29

29. **B** - FIDO2 keys are inherently resistant to phishing attacks because the authentication credentials are cryptographically bound to the specific origin (domain name) of the relying party.

**Explanation:** SMS-based OTPs are susceptible to various attacks, including SIM swapping, SS7 interception, and particularly phishing (where a user is tricked into entering the OTP on a fake site). FIDO2/WebAuthn provides strong, phishing-resistant authentication because the generated public-key credentials are bound to the relying party's origin (e.g., `example.com`). If a user is on a phishing site (e.g., `examp1e.com`), the browser and the authenticator will not release the credentials for the legitimate site, effectively stopping the attack. This origin binding is a core security property that SMS OTPs lack.
