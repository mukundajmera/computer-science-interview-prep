# Back-of-Envelope Estimation for System Design

Fast estimation is a core interview skill. The goal is not perfect math — it is to produce reasonable sizing inputs for architecture decisions.

---

## Quick Numbers to Remember

- 1 day = 86,400 seconds
- 1 million/day ≈ 12 requests/second
- 100 million/day ≈ 1,157 requests/second
- 1 KB ≈ 10^3 bytes (interview approximation)
- 1 GB ≈ 10^9 bytes

Use rounded values; keep arithmetic easy and auditable.

---

## 6-Step Estimation Flow

1. **Assume DAU / MAU**
2. **Estimate actions per user/day**
3. **Convert to average QPS**
4. **Apply peak factor** (e.g., 3x to 5x)
5. **Estimate payload size**
6. **Project storage growth** (daily/monthly/yearly)

---

## Example: URL Shortener (simplified)

Assume:
- 50M new URLs/day
- 500M redirects/day
- 300 bytes metadata per URL

Then:
- Write QPS ≈ 50M / 86,400 ≈ 580
- Read QPS ≈ 500M / 86,400 ≈ 5,800
- New storage/day ≈ 50M × 300B ≈ 15 GB/day

This immediately suggests:
- read-heavy optimization (cache)
- write path idempotency
- partitioning plan for long-term growth

---

## Example: Feed Service (simplified)

Assume:
- 100M DAU
- 5 posts/user/day
- average post metadata 1 KB

Writes/day = 500M ⇒ ~5,800 writes/sec average  
At 4x peak ⇒ ~23K writes/sec peak

Use this to reason about:
- fan-out strategy
- queue throughput
- timeline cache pressure

---

## Interview Tips

- State assumptions explicitly: "I’ll assume..."
- Keep units visible in each step.
- Round aggressively to avoid arithmetic mistakes.
- Re-check order of magnitude at the end.

---

## Common Mistakes

- Jumping to architecture before sizing.
- Mixing MB/MiB or decimal/binary units inconsistently.
- Forgetting peak traffic multiplier.
- Estimating storage without retention window.

---

## Practice Prompts

Try estimating for:
1. Chat app messages/day and storage/year
2. Video upload bandwidth and transcoding throughput
3. Ride matching request QPS in a metro region

---

## Related Reading

- [CAP Theorem](./cap-theorem.md)
- [URL Shortener HLD](../../04-hld-projects/url-shortener/DESIGN.md)
- [CONCEPTS.md](../../CONCEPTS.md)
- [Horizontal vs Vertical Scaling](./horizontal-vs-vertical-scaling.md)
- [Caching](../../03-hld-concepts/caching/)
- [CDN](../../03-hld-concepts/cdn/)
# Back-of-Envelope Estimation

Back-of-envelope estimation helps you sanity-check architecture choices quickly during system design interviews.

---

## 🎯 Why It Matters

Before discussing components, estimate:
- Traffic (QPS)
- Storage growth
- Bandwidth
- Memory/cache footprint

This prevents unrealistic designs and helps justify trade-offs.

---

## 🧮 Common Numbers to Remember

| Metric | Rule of Thumb |
|--------|----------------|
| 1 KB | 10^3 bytes |
| 1 MB | 10^6 bytes |
| 1 GB | 10^9 bytes |
| 1 TB | 10^12 bytes |
| 1 day | 86,400 seconds |
| 1 month | ~2.6 million seconds |

---

## 🛠️ Estimation Workflow

1. **Start with users** (DAU/MAU)
2. **Convert to requests/sec**
3. **Estimate read/write split**
4. **Compute storage per object**
5. **Project growth** (daily/monthly/yearly)
6. **Add headroom** (typically 2-5x)

---

## 📌 Example: URL Shortener

Assumptions:
- 10M new URLs/day
- Average record size = 500 bytes
- Read:write ratio = 100:1

Calculations:
- **Write QPS** = 10,000,000 / 86,400 ≈ 116 writes/sec
- **Read QPS** = 116 × 100 = 11,600 reads/sec
- **Daily storage** = 10,000,000 × 500 B = 5 GB/day
- **Yearly storage** = 5 × 365 ≈ 1.8 TB/year

Interpretation:
- Writes are moderate; reads dominate
- Strong candidate for aggressive caching + CDN

---

## 📦 Capacity Planning Cheats

### Storage
`total_storage = objects_per_day × bytes_per_object × retention_days`

### Bandwidth
`egress_per_sec = responses_per_sec × avg_payload_bytes`

### Cache memory
`cache_memory = hot_keys × avg_value_size × overhead_factor`

Use overhead factor (1.2-2.0) for metadata, pointers, fragmentation.

---

## ⚠️ Common Mistakes

- Mixing binary and decimal units without clarity
- Ignoring peak traffic (using only average QPS)
- Forgetting replication factor in storage estimate
- Not adding growth and safety buffer
- Overfitting to exact numbers instead of order-of-magnitude

---

## 🧠 Interview Tips

- State assumptions clearly and keep them simple
- Round numbers for speed (e.g., 86,400 ≈ 100k seconds/day for quick pass)
- Use ranges when uncertain
- Revisit estimates after architecture decisions

---

## 🔗 Cross-References

- [Horizontal vs Vertical Scaling](./horizontal-vs-vertical-scaling.md)
- [Caching](../../03-hld-concepts/caching/)
- [CDN](../../03-hld-concepts/cdn/)

---

*💡 Pro Tip: Interviewers care less about exact math and more about your assumptions, sanity checks, and whether your architecture follows from your numbers.*
