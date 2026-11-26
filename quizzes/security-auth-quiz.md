# Security & Auth Quiz

29 questions focused on security-auth.

Time: 35 minutes
Difficulty: Medium-Hard

---

## Section 1: Core Concepts

### Question 1
Which OAuth 2.0 grant type is considered the most secure for web applications with a backend server?

A) Authorization Code Grant
B) Resource Owner Password Credentials Grant
C) Client Credentials Grant
D) Implicit Grant

### Question 2
What is the primary purpose of OpenID Connect (OIDC) on top of OAuth 2.0?

A) To encrypt the data payload of API requests automatically.
B) To manage fine-grained database permissions within the authorization server.
C) To provide authentication and identity verification, resulting in an ID Token.
D) To replace the Authorization Code Grant with a faster protocol.

### Question 3
What are the three parts of a JSON Web Token (JWT)?

A) Public Key, Private Key, and Certificate.
B) Client ID, Client Secret, and Expiration Time.
C) Subject, Issuer, and Audience.
D) Header, Payload, and Signature.

### Question 4
How can a server securely verify a JWT without calling the authorization server?

A) By decoding the payload from Base64 and checking if the 'is_valid' flag is true.
B) By storing a copy of all issued JWTs in a local database and checking if the received token exists in that database.
C) By using the pre-shared secret or the authorization server's public key to cryptographically validate the JWT's signature.
D) By sending an HTTP HEAD request to the client's IP address.

### Question 5
Which of the following describes the difference between Symmetric and Asymmetric encryption?

A) Symmetric encryption does not require a key, whereas asymmetric encryption requires two keys.
B) Symmetric encryption is only used for data at rest, while asymmetric encryption is only used for data in transit.
C) Symmetric encryption uses the same key for both encryption and decryption, while asymmetric encryption uses a public key to encrypt and a private key to decrypt.
D) Symmetric encryption is significantly slower but more secure than asymmetric encryption.

### Question 6
What is the primary benefit of Mutual TLS (mTLS) over standard TLS?

A) It requires both the client and the server to authenticate each other using cryptographic certificates.
B) It eliminates the need for Certificate Authorities (CAs) by using a decentralized blockchain.
C) It allows HTTP traffic to bypass firewalls by tunneling over UDP.
D) It doubles the encryption strength by using two different cipher suites simultaneously.

### Question 7
Which vulnerability occurs when an attacker tricks a user's browser into executing unwanted actions on a trusted site where the user is currently authenticated?

A) Server-Side Request Forgery (SSRF)
B) SQL Injection
C) Cross-Site Request Forgery (CSRF)
D) Cross-Site Scripting (XSS)

### Question 8
What is the most robust defense against Cross-Site Scripting (XSS) attacks?

A) Disabling all JavaScript execution in the user's browser.
B) Encrypting all HTTP responses using AES-256.
C) Context-aware output encoding/escaping and implementing a strong Content Security Policy (CSP).
D) Relying solely on Web Application Firewalls (WAF) to filter incoming requests.

### Question 9
How do Anti-CSRF Tokens (Synchronizer Tokens) prevent CSRF attacks?

A) The server encrypts the user's session cookie with a rotating private key.
B) The server verifies that the 'Referer' header strictly matches the 'Origin' header.
C) The browser automatically blocks any POST requests originating from a different domain.
D) The server generates a unique, unpredictable token that the client must include in the body or header of every state-changing request, which attackers cannot predict or read.

### Question 10
In OAuth 2.0, what is the role of the 'Refresh Token'?

A) To revoke all active sessions across multiple devices simultaneously.
B) To securely transmit the user's username and password to the authorization server.
C) To digitally sign API requests to prove they originated from the authorized client.
D) To allow the client application to obtain a new access token without requiring the user to re-authenticate, after the current access token expires.

### Question 11
Why is the OAuth 2.0 'Implicit Grant' flow now considered deprecated and insecure for Single-Page Applications (SPAs)?

A) It cannot support external identity providers like Google or Facebook.
B) It returns the access token directly in the URL fragment (hash), exposing it to browser history, logs, and potential XSS attacks.
C) It requires the user to memorize a complex 64-character alphanumeric code.
D) It relies entirely on symmetric encryption, making it vulnerable to quantum computing attacks.

### Question 12
What is Proof Key for Code Exchange (PKCE) in the context of OAuth 2.0?

A) A specific type of hardware security module (HSM) used to store client secrets.
B) An extension to the Authorization Code flow that prevents authorization code interception attacks, especially in public clients like mobile apps and SPAs.
C) A protocol that replaces OAuth 2.0 for IoT devices with limited processing power.
D) A mechanism for encrypting the JWT payload using the client's public key.

### Question 13
What is the principle of 'Least Privilege'?

A) A user, process, or system should only be given the bare minimum permissions necessary to perform its intended function.
B) Web applications should completely disable firewalls for internal APIs to maximize performance.
C) Passwords should have the shortest possible length to encourage frequent rotation.
D) Database administrators should share a single root account to minimize the number of accounts to manage.

### Question 14
How does setting the 'HttpOnly' flag on a cookie enhance security?

A) It forces the browser to only transmit the cookie over encrypted HTTPS connections.
B) It automatically prevents the cookie from being sent in cross-site requests, stopping CSRF attacks.
C) It prevents client-side scripts (like JavaScript) from accessing the cookie, mitigating the risk of cookie theft via XSS attacks.
D) It encrypts the cookie's contents using the server's private key before sending it to the browser.

### Question 15
Which of the following is a common method for handling JWT revocation, considering JWTs are inherently stateless?

A) Sending an HTTP DELETE request to the client's browser to physically remove the token from localStorage.
B) Stateless JWTs cannot be revoked under any circumstances; you must simply wait for them to expire.
C) Modifying the JWT signature on the fly to render it invalid.
D) Maintaining a centralized 'denylist' (or blocklist) of revoked token signatures or IDs (jti) that the resource server must check, often stored in a fast cache like Redis.

### Question 16
What does the 'SameSite=Strict' attribute on a cookie do?

A) It instructs the browser to never send the cookie with cross-site requests, providing robust protection against CSRF attacks.
B) It limits the cookie's lifespan to a single browsing session, deleting it when the browser closes.
C) It requires the user to input a multi-factor authentication code before the cookie can be read.
D) It restricts the cookie to only be accessible by the specific subdomain that set it.

### Question 17
In Public Key Infrastructure (PKI), what is the role of a Certificate Authority (CA)?

A) To digitally sign a server's public key, asserting that the key belongs to the legitimate owner of the domain name.
B) To generate symmetric session keys for clients and servers during the TLS handshake.
C) To monitor network traffic for DDoS attacks and automatically block malicious IPs.
D) To store plaintext passwords securely on behalf of users.

### Question 18
What is 'Salt' in the context of password hashing, and why is it used?

A) A secondary password required only during password resets to verify identity.
B) An encryption algorithm that continuously changes its keys over time to prevent brute-force attacks.
C) A specialized hardware chip used to accelerate cryptographic operations on a server.
D) A random string of data appended to a password before hashing, used to ensure identical passwords have unique hashes and to defend against rainbow table attacks.

### Question 19
What is Server-Side Request Forgery (SSRF)?

A) An attack where a malicious server pretends to be a client to steal data from a legitimate server.
B) A vulnerability where an attacker tricks a server into making HTTP requests to internal or external systems on their behalf, often bypassing firewalls.
C) A technique for forging digital signatures on server-to-server API calls.
D) A database exploit that allows attackers to modify the structure of server-side tables.

### Question 20
What is the difference between Authentication and Authorization?

A) Authentication verifies the identity of a user (who they are), while Authorization determines what permissions the user has (what they can do).
B) Authentication relies entirely on passwords, while Authorization relies exclusively on biometric data.
C) Authentication determines what a user can access, while Authorization verifies the user's identity.
D) Authentication is used for internal network access, while Authorization is used for public web access.

### Question 21
Which cryptographic concept provides 'Non-repudiation'?

A) Symmetric AES-256 Encryption.
B) Diffie-Hellman Key Exchange.
C) Secure Hashing Algorithms (like SHA-256).
D) Digital Signatures created using Asymmetric Encryption.

### Question 22
What is a 'Rainbow Table' attack?

A) A DDoS attack targeting multiple geographic regions simultaneously to disrupt global routing tables.
B) An attack that uses a massive pre-computed database of plaintext passwords and their corresponding hashes to quickly reverse hashed passwords.
C) A social engineering technique where attackers present a spectrum of deceptive scenarios to trick a user.
D) An exploit utilizing colored light frequencies to interfere with fiber-optic data transmission.

### Question 23
In a microservices architecture, what is a common pattern for propagating user identity and permissions between internal services?

A) Passing a signed JWT (JSON Web Token) in the 'Authorization' header of every service-to-service HTTP request.
B) Having each microservice independently redirect the user to the login page for every internal API call.
C) Encoding the user's plain-text password into the URL path of every internal request.
D) Using a shared, globally accessible in-memory database that stores a boolean 'is_authorized' flag for every request.

### Question 24
What is the purpose of the 'Audience' (aud) claim in a JWT?

A) It tracks the number of times the token has been viewed or validated by a server.
B) It identifies the specific recipients (or resource servers) that the JWT is intended for, preventing a token issued for one API from being used against a completely different API.
C) It specifies the cryptographic algorithm used to generate the token's signature.
D) It defines the geographical region where the token is legally allowed to be processed.

### Question 25
How does a Web Application Firewall (WAF) differ from a traditional Network Firewall?

A) A WAF is entirely hardware-based, whereas a Network Firewall is exclusively a software application.
B) A WAF operates at Layer 7 (Application Layer) to analyze HTTP traffic for web-specific attacks like SQL injection and XSS, whereas a Network Firewall operates at Layers 3/4 to block IP addresses and ports.
C) A WAF encrypts traffic leaving the server, while a Network Firewall decrypts incoming traffic.
D) A WAF can only protect internal Intranets, while a Network Firewall only protects against external Internet traffic.

### Question 26
When designing an authentication system that relies on JSON Web Tokens (JWT) for stateless authorization across microservices, what is the most critical vulnerability introduced if the system fails to enforce the 'alg' (algorithm) header validation?

A) An attacker can change the algorithm to 'none', allowing them to forge tokens without needing the secret key, granting unauthorized access.
B) The authorization server will automatically fall back to basic authentication, transmitting passwords in plaintext over the network.
C) The JWT payload size will exceed HTTP header limits, causing all API requests to fail with a 413 Payload Too Large error.
D) The system will become susceptible to Cross-Site Scripting (XSS) attacks because the token signature cannot be rendered safely in the browser.



### Question 27
What is the primary purpose of Cross-Origin Resource Sharing (CORS) in web security?

A) To encrypt data transmitted between a client's browser and a third-party API.
B) To prevent servers from being overwhelmed by Distributed Denial of Service (DDoS) attacks from multiple origins.
C) To relax the browser's Same-Origin Policy in a controlled manner, allowing a web application running at one origin to access restricted resources from a different origin.
D) To automatically block all requests originating from domains with a poor reputation score.


### Question 28
Which mechanism is the most effective defense against Cross-Site Request Forgery (CSRF) in a traditional session-based web application?

A) Storing the session ID exclusively in an HttpOnly cookie so JavaScript cannot read it.
B) Implementing a Content Security Policy (CSP) that restricts script sources to self.
C) Requiring a synchronized, cryptographically strong random anti-CSRF token in every state-changing request (e.g., POST, PUT, DELETE).
D) Validating the HTTP User-Agent header on every incoming request.


### Question 29
In the context of multi-factor authentication (MFA), what is the primary security advantage of using a FIDO2/WebAuthn hardware security key over SMS-based One-Time Passwords (OTPs)?

A) FIDO2 keys rely on symmetric cryptography, making them faster to validate on the server side compared to generating SMS OTPs.
B) FIDO2 keys are inherently resistant to phishing attacks because the authentication credentials are cryptographically bound to the specific origin (domain name) of the relying party.
C) FIDO2 keys automatically sync their private keys to the cloud, ensuring users never lose access to their accounts if a key is misplaced.
D) SMS OTPs are transmitted over encrypted cellular networks, making them vulnerable to Man-in-the-Middle (MitM) attacks, whereas FIDO2 keys use plain text over USB.
