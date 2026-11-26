# Design Approach for File Storage Service

---

## 1. Requirements Clarification

### Assumptions with Numbers

| Metric | Value |
|--------|-------|
| DAU | 100 million |
| Files per user | 1,000 average |
| Total files | 500 billion |
| Average file size | 1 MB |
| Total storage | 500 PB |

---

## 2. Back-of-the-Envelope Estimation

### Storage Calculations

```
Total files: 500M users * 1000 files = 500 billion files
Total storage: 500B * 1 MB = 500 PB
Daily uploads: 1 billion files/day
Upload throughput: 1B / 86400 = ~11,500 files/sec
```

### Metadata Size

```
Per file metadata: ~1 KB
Total metadata: 500B * 1 KB = 500 TB
```

---

## 3. API Design

### Upload File
```
POST /api/v1/files/upload
Headers: Content-Type: multipart/form-data
Body: file data + metadata
Response: { fileId, uploadUrl, chunks: [...] }
```

### Chunked Upload
```
POST /api/v1/files/{fileId}/chunks/{chunkNum}
Body: chunk data
Response: { status, uploaded: 5/10 }
```

### Download File
```
GET /api/v1/files/{fileId}/download
Response: Redirect to CDN URL or stream content
```

---

## 4. High-Level Architecture

```
Client -> API Gateway -> File Service -> Metadata DB
                      -> Block Service -> Object Storage (S3)
                      -> Sync Service -> Change Queue
```

### Components

1. **File Service**: Handles metadata operations
2. **Block Service**: Manages file chunks
3. **Object Storage**: S3/GCS for blob storage
4. **Metadata DB**: PostgreSQL for file metadata
5. **CDN**: CloudFront for downloads

---

## 5. Deep Dives

### 5.1 Chunked Upload

```
Chunk Size: 4 MB
Process:
1. Client requests upload session
2. Server returns upload URLs for each chunk
3. Client uploads chunks in parallel
4. Server assembles and verifies
```

### 5.2 Deduplication

```
Strategy: Content-based hashing
- Calculate SHA-256 of each block
- Store only unique blocks
- Multiple files can reference same blocks
Savings: 30-50% storage reduction
```

### 5.3 CDN Integration

```
Download flow:
1. Client requests file download
2. Generate signed CDN URL
3. Client downloads from nearest edge
4. Cache popular files at edge
```

---

## 6. Trade-offs

### Strong vs Eventual Consistency

| Choice | Implication |
|--------|-------------|
| **Chose: Strong for metadata** | Users see consistent file list |
| Trade-off | Slightly higher latency |
| Benefit | No sync conflicts |

---

## 7. Evolution Plan

**v1-basic:** Direct upload/download, no chunking
**v2-scaled:** Chunked uploads, CDN, caching
**v3-distributed:** Deduplication, multi-region, real-time sync
