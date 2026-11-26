# Interview Questions: Large Blob Handling

## Basic

### 1. Why avoid proxying large files through app servers?
**A:** It increases latency/cost and creates unnecessary bottlenecks; servers should handle authorization and metadata, not bulk byte transfer.

### 2. What is a presigned URL?
**A:** A time-limited, scoped URL that grants direct storage access for a specific operation.

### 3. Why use multipart upload?
**A:** It allows resumable transfer and retry of failed parts only.

### 4. Where should file metadata live?
**A:** In the primary database, separate from object-store bytes.

## Intermediate

### 5. How do you keep metadata status correct?
**A:** Create pending metadata at session start, mark completion via storage events, and run reconciliation for missed events.

### 6. How do you prevent abuse?
**A:** Signed URL constraints (size/type), quarantine bucket, malware/content scan, and publish only after validation.

### 7. What cleanup is required for multipart uploads?
**A:** Lifecycle cleanup of incomplete sessions to avoid storage leakage.

### 8. How do you optimize large downloads globally?
**A:** CDN edge caching plus range requests for resumable and seekable retrieval.

## Advanced

### 9. When should direct upload not be used?
**A:** When synchronous inline inspection/compliance requires data to pass through controlled systems.

### 10. How do you model idempotent completion?
**A:** Tie completion to upload session ID + expected part list/checksums and ensure repeated completion calls are safe.

### 11. How do you support high fanout of shared files?
**A:** Cacheable signed delivery policy, CDN TTL tuning, and controlled invalidation for revoked content.

### 12. Strong trade-off statement?
**A:** "I move bytes off app servers for scale, then recover consistency with event-confirmed state and reconciliation."
