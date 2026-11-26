# CDN HLD Interview Follow-Ups

## Mandatory Interview Baseline
*These are standard probes candidates should expect during the main 45-minute session.*

1. **How do you handle HTTPS/TLS termination at the edge?**
   - *Expected:* Edge nodes must hold the customer's TLS certificate. To do this securely at scale without distributing private keys to 10,000 nodes, use Keyless SSL (where edge nodes perform the symmetric key exchange, but the private key operation is done by a centralized secure key server) or heavily restricted short-lived proxy certs.

2. **What happens if the Origin Shield region goes down?**
   - *Expected:* Edge PoPs must failover to a secondary Origin Shield in a different region, or, as a last resort, fetch directly from the Customer Origin, though this risks overwhelming it if caches are cold.

3. **How do you prevent malicious users from bypassing the cache with random query parameters (e.g., `?cb=123`)?**
   - *Expected:* Implement Cache Key Normalization at the Edge Router. Strip unknown or unapproved query parameters before hashing the URL to check the cache.

---

## Optional Staff Follow-ups
*These represent L6+ complexity and are only introduced if the candidate breezes through the baseline.*

1. **Adaptive Bitrate Streaming (ABR):** How would you modify the CDN to handle dynamic video quality switching based on client network conditions?
2. **Edge Compute Integration:** If we allow customers to run WebAssembly (Wasm) functions at the edge to modify requests/responses, how does this impact the cache key lifecycle and request coalescing?
3. **Thundering Herd on Purge:** Even with coalescing, a massive global purge of thousands of keys can spike CPU on the Origin Shield. How do you implement rate-limiting or priority queues for cache fills?
