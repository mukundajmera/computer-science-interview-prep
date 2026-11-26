# Pastebin - Follow-Up Questions

Interviews rarely stop at the basic design. Expect the interviewer to probe your architecture with these follow-up questions.

> **Related docs:** [PROBLEM](./PROBLEM.md) · [DESIGN](./DESIGN.md) · [APPROACH](./APPROACH.md) · [RUBRIC](./RUBRIC.md) · [STRONG-ANSWER](./STRONG-ANSWER.md) · [PITFALLS](./PITFALLS.md) · [COMPARISON](./COMPARISON.md)

---

## Follow-up questions

### 1. How do you handle a "viral" paste that gets 100,000 hits per second?
*What they are looking for:* Understanding of layered caching.
*Strong Answer:*
- **CDN:** Push caching to the edge. Since pastes are immutable (mostly), configuring a CDN like Cloudflare to cache the GET responses heavily shields our origin.
- **Redis Cache:** For requests that bypass the CDN, Redis absorbs the load.
- **In-Memory Cache:** If Redis becomes a bottleneck (hot key problem), we introduce a small, short-lived (e.g., 5 seconds) local LRU cache directly on the API application servers.

### 2. How can we implement "Burn After Reading" (One-Time-Use pastes)?
*What they are looking for:* Concurrency and atomic operations.
*Strong Answer:*
We need to ensure that concurrent read requests do not both receive the paste before it is deleted.
- We can use a Redis `GETDEL` command or a DB transaction with `SELECT ... FOR UPDATE` followed by a `DELETE`.
- The first request successfully retrieves and deletes; subsequent concurrent requests find the record missing and receive a 404.

### 3. If we move to a NoSQL database for metadata, how does the Key Generation Service (KGS) change?
*What they are looking for:* Understanding of consistency models.
*Strong Answer:*
In SQL, we rely on ACID guarantees and unique constraints. In NoSQL (like Cassandra), which is eventually consistent, unique constraints are hard. The KGS becomes even more critical because it is the *only* source of uniqueness. We would manage the KGS pool in a strongly consistent store (like ZooKeeper/etcd or a dedicated small SQL DB) while the actual paste metadata scales out horizontally in NoSQL.

## Variants and extensions

### A. End-to-End Encryption
*Scenario:* Users want to store sensitive data (passwords, secrets) that not even the server administrators can read.
*Design adjustments:*
- The encryption must happen *client-side* (in the browser).
- The client generates a random AES key, encrypts the text, and uploads the ciphertext to the server.
- The decryption key is appended to the URL as a URL fragment (e.g., `pastebin.com/xyz123#SecureKey`).
- Browsers do not send URL fragments to the server, so the server never sees the key. When the link is opened, client-side JS extracts the fragment and decrypts the fetched ciphertext.

### B. Custom Aliases
*Scenario:* A user wants a custom URL like `pastebin.com/my-custom-url` instead of a random ID.
*Design adjustments:*
- Add a `custom_alias` column to the DB with a `UNIQUE` constraint.
- If a collision occurs on insert, return a `409 Conflict` to the user.
- The read path checks the DB for either `short_key` OR `custom_alias`.

## Interviewer probes to prepare

- **Storage Costs:** "S3 is getting expensive. How do we reduce costs for older pastes that haven't expired but are rarely read?"
  *Answer:* Implement object lifecycle policies in S3 to move files older than 30 days to cheaper, colder storage tiers like S3 Infrequent Access or Glacier.
- **Abuse:** "People are uploading copyrighted material or malware links. How do we stop this?"
  *Answer:* Integrate an async background queue (Kafka). Upon paste creation, publish an event. A moderation worker consumes the text, runs it through a regex/ML spam filter or Google Safe Browsing API, and sets a `flagged` status in the DB if malicious.
