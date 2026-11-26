# File Storage Service System Design

Complete high-level design for a cloud file storage and sync service (like Dropbox/Google Drive).

---


## Requirements

### Functional Requirements
- Core user flow for File Storage Service.

### Non-Functional Requirements
- High availability, low latency, fault tolerance.

## Back-of-envelope Estimation

### Traffic
| Metric | Calculation | Result |
|---|---|---|
| DAU | Given | 50M |
| Avg QPS | 50M DAU x 4 files / 86,400 s | 2.3K avg QPS |
| Peak QPS | 2.3K avg QPS x 3 peak | 6.9K peak QPS |

### Storage
| Metric | Calculation | Result |
|---|---|---|
| Daily Storage | 50M DAU x 4 files x 2 MB = 400 TB/day |

## API Contracts

### Endpoints
```http
POST /api/v1/files/upload
GET /api/v1/files/download
```

## Data Model

### Schema
- Primary Key: `file_id`
- Partition Key: `user_id`


## System Architecture

```mermaid
flowchart TB
    subgraph Clients["Client Applications"]
        Desktop[Desktop App<br/>Windows/Mac/Linux]
        Mobile[Mobile App<br/>iOS/Android]
        Web[Web Browser]
    end
    
    subgraph Edge["Edge Layer"]
        CDN[CloudFront CDN<br/>Static Assets + Downloads]
        DNS[Route 53<br/>GeoDNS]
    end
    
    subgraph Gateway["API Gateway Layer"]
        LB[Application Load Balancer]
        RL[Rate Limiter]
        Auth[Auth Service<br/>OAuth 2.0]
    end
    
    subgraph Services["Core Services"]
        FileService[File Service<br/>Metadata CRUD]
        BlockService[Block Service<br/>Chunking + Dedup]
        SyncService[Sync Service<br/>Conflict Resolution]
        ShareService[Share Service<br/>Permissions]
        SearchService[Search Service<br/>Full-text]
    end
    
    subgraph Queue["Message Queue"]
        Kafka[Kafka Cluster]
        SyncTopic[Sync Events Topic]
        IndexTopic[Index Events Topic]
    end
    
    subgraph Cache["Caching Layer"]
        MetaCache[(Metadata Cache<br/>Redis)]
        SessionCache[(Upload Sessions<br/>Redis)]
        TreeCache[(Folder Tree Cache<br/>Redis)]
    end
    
    subgraph Storage["Storage Layer"]
        MetadataDB[(Metadata DB<br/>PostgreSQL)]
        BlockStore[(Block Store<br/>S3)]
        SearchIndex[(Search Index<br/>Elasticsearch)]
    end
    
    subgraph Sync["Sync Infrastructure"]
        WebSocket[WebSocket Gateway<br/>Real-time Sync]
        NotifService[Notification Service]
    end
    
    Desktop --> DNS
    Mobile --> DNS
    Web --> CDN
    CDN --> DNS
    DNS --> LB
    LB --> RL
    RL --> Auth
    
    Auth --> FileService
    Auth --> BlockService
    Auth --> ShareService
    Auth --> SyncService
    
    FileService --> MetadataDB
    FileService --> MetaCache
    FileService --> Kafka
    
    BlockService --> BlockStore
    BlockService --> SessionCache
    
    SyncService --> WebSocket
    SyncService --> TreeCache
    
    Kafka --> SyncService
    Kafka --> SearchService
    SearchService --> SearchIndex
    
    WebSocket --> Desktop
    WebSocket --> Mobile
    
    BlockStore --> CDN
    
    style BlockStore fill:#69db7c
    style MetadataDB fill:#74c0fc
    style Kafka fill:#ffa94d
```

**Architecture Notes:**
- **Block Storage**: Files split into 4MB chunks, stored in S3 with content-addressed naming
- **Deduplication**: SHA-256 hash of blocks enables cross-user dedup (30-40% storage savings)
- **Sync Model**: Event-driven with WebSocket push for real-time updates
- **CDN**: Serves public/shared files and download acceleration
- **Multi-region**: Active-active with CRDTs for conflict resolution

---

## Sequence Diagrams

### Upload Flow: Chunked Upload with Deduplication

```mermaid
sequenceDiagram
    autonumber
    participant Client as Desktop Client
    participant API as API Gateway
    participant FileService
    participant BlockService
    participant S3 as Block Store (S3)
    participant MetaDB as PostgreSQL
    participant Kafka
    participant SyncService
    participant WebSocket
    
    Client->>Client: Split file into 4MB chunks
    Client->>Client: Calculate SHA-256 for each chunk
    
    Client->>API: POST /files/upload-session {filename, size, blockHashes[]}
    API->>FileService: Create upload session
    FileService->>BlockService: Check existing blocks by hash
    BlockService->>MetaDB: Query blocks by hash
    MetaDB-->>BlockService: Existing block IDs
    BlockService-->>FileService: {existingBlocks[], missingHashes[]}
    FileService->>MetaDB: Create upload_session record
    FileService-->>Client: {sessionId, missingChunks[], presignedUrls[]}
    
    Note over Client,S3: Upload only missing chunks (dedup savings)
    
    loop For each missing chunk
        Client->>S3: PUT to pre-signed URL
        S3-->>Client: 200 OK
        Client->>API: POST /upload-session/{id}/chunk-complete
        API->>BlockService: Register new block
        BlockService->>MetaDB: Insert block record
    end
    
    Client->>API: POST /upload-session/{id}/complete
    API->>FileService: Complete upload
    FileService->>MetaDB: Create file record, link blocks
    FileService->>Kafka: Publish FileCreated event
    FileService-->>Client: {fileId, version, url}
    
    Note over Kafka,WebSocket: Sync to other devices
    
    Kafka->>SyncService: FileCreated event
    SyncService->>WebSocket: Push to user's devices
    WebSocket-->>Client: Sync notification
```

### Download Flow with CDN and Range Requests

```mermaid
sequenceDiagram
    autonumber
    participant Client as Desktop Client
    participant CDN as CloudFront
    participant API as API Gateway
    participant FileService
    participant BlockService
    participant S3 as Block Store
    participant MetaDB as PostgreSQL
    
    Client->>API: GET /files/{fileId}/download
    API->>FileService: Get download URL
    FileService->>MetaDB: Get file metadata + blocks
    MetaDB-->>FileService: File info, block list
    
    alt File is public/shared
        FileService-->>Client: Redirect to CDN URL
        Client->>CDN: GET file
        alt CDN cache hit
            CDN-->>Client: File content (cached)
        else CDN cache miss
            CDN->>S3: Fetch blocks
            S3-->>CDN: Block content
            CDN->>CDN: Assemble and cache
            CDN-->>Client: File content
        end
    else File is private
        FileService->>FileService: Generate signed URL (expires 1h)
        FileService-->>Client: {signedUrl, blocks[]}
        
        loop For each block (parallel)
            Client->>S3: GET block with signed URL
            S3-->>Client: Block content
        end
        Client->>Client: Assemble file from blocks
    end
```

### Sync Flow with Conflict Resolution

```mermaid
sequenceDiagram
    autonumber
    participant ClientA as Device A
    participant ClientB as Device B
    participant WebSocket as WebSocket Gateway
    participant SyncService
    participant FileService
    participant MetaDB as PostgreSQL
    
    Note over ClientA,ClientB: Both devices modify same file offline
    
    ClientA->>SyncService: Push changes {fileId, version: 3, changes}
    SyncService->>MetaDB: Get current version
    MetaDB-->>SyncService: Current version: 3
    SyncService->>MetaDB: Update to version 4
    SyncService->>WebSocket: Broadcast to user devices
    WebSocket-->>ClientB: Sync event {fileId, version: 4}
    
    ClientB->>SyncService: Push changes {fileId, version: 3, changes}
    SyncService->>MetaDB: Get current version
    MetaDB-->>SyncService: Current version: 4 (conflict!)
    
    alt Auto-resolvable conflict
        SyncService->>SyncService: Apply CRDT merge rules
        SyncService->>MetaDB: Save merged version 5
        SyncService->>WebSocket: Broadcast version 5
        WebSocket-->>ClientA: Sync version 5
        WebSocket-->>ClientB: Sync version 5
    else Manual resolution needed
        SyncService->>FileService: Create conflict copy
        FileService->>MetaDB: Save as "filename (conflict).ext"
        SyncService->>WebSocket: Notify conflict
        WebSocket-->>ClientA: Conflict notification
        WebSocket-->>ClientB: Conflict notification
    end
```

---

## Entity-Relationship Diagram

```mermaid
erDiagram
    USER ||--o{ FILE : owns
    USER ||--o{ SHARE : creates
    FILE ||--o{ FILE_VERSION : has
    FILE ||--o{ FILE_BLOCK : composed_of
    BLOCK ||--o{ FILE_BLOCK : referenced_by
    FOLDER ||--o{ FILE : contains
    FOLDER ||--o{ FOLDER : contains
    USER ||--o{ FOLDER : owns
    SHARE }o--o| FILE : shares
    SHARE }o--o| FOLDER : shares
    USER ||--o{ DEVICE : owns
    DEVICE ||--o{ SYNC_CURSOR : tracks

    USER {
        uuid user_id PK
        string email UK
        string password_hash
        bigint storage_used "Bytes used"
        bigint storage_quota "Max bytes"
        string plan "free/pro/business"
        timestamp created_at
    }

    FOLDER {
        uuid folder_id PK
        uuid user_id FK
        uuid parent_folder_id FK "NULL for root"
        string name
        string path "Full path for search"
        timestamp created_at
        timestamp updated_at
    }

    FILE {
        uuid file_id PK
        uuid user_id FK
        uuid folder_id FK
        string name
        string extension
        string mime_type
        bigint size_bytes
        string content_hash "SHA-256 of content"
        int current_version
        boolean is_deleted "Soft delete"
        timestamp created_at
        timestamp updated_at
        timestamp deleted_at
    }

    FILE_VERSION {
        uuid version_id PK
        uuid file_id FK
        int version_number
        bigint size_bytes
        string content_hash
        uuid modified_by FK "User who modified"
        string change_type "created/modified/restored"
        timestamp created_at
    }

    BLOCK {
        uuid block_id PK
        string content_hash UK "SHA-256"
        string storage_path "S3 key"
        bigint size_bytes
        int reference_count "For garbage collection"
        timestamp created_at
    }

    FILE_BLOCK {
        uuid file_id FK
        int version_number FK
        int block_index "Order in file"
        uuid block_id FK
    }

    SHARE {
        uuid share_id PK
        uuid owner_id FK
        uuid file_id FK "NULL if folder"
        uuid folder_id FK "NULL if file"
        string share_type "link/email/domain"
        string permission "view/edit"
        string access_token UK "For link shares"
        string recipient_email "For email shares"
        timestamp expires_at
        timestamp created_at
    }

    DEVICE {
        uuid device_id PK
        uuid user_id FK
        string device_name
        string device_type "desktop/mobile/web"
        string os "windows/macos/ios/android"
        timestamp last_sync_at
        boolean is_active
    }

    SYNC_CURSOR {
        uuid cursor_id PK
        uuid device_id FK
        uuid folder_id FK "Root folder synced"
        bigint cursor_position "Event sequence number"
        timestamp updated_at
    }

    UPLOAD_SESSION {
        uuid session_id PK
        uuid user_id FK
        uuid folder_id FK
        string filename
        bigint total_size
        int total_chunks
        int uploaded_chunks
        string status "pending/uploading/complete/failed"
        timestamp created_at
        timestamp expires_at
    }
```

**Schema Notes:**
- **Partitioning**: 
  - `FILE` partitioned by `user_id` for user-centric queries
  - `BLOCK` partitioned by `content_hash` prefix for distribution
- **Deduplication**: 
  - `BLOCK.content_hash` unique constraint enables cross-user dedup
  - `reference_count` tracks how many files use each block
- **Soft Deletes**: 
  - `FILE.is_deleted` + `deleted_at` for trash/recovery (30 days)
- **Versioning**: 
  - `FILE_VERSION` keeps history, linked to blocks via `FILE_BLOCK`
- **Indexes**:
  - `FILE(user_id, folder_id, name)` for folder listing
  - `FILE(user_id, updated_at DESC)` for recent files
  - `BLOCK(content_hash)` for dedup lookup
  - `SHARE(access_token)` for link validation
  - `SYNC_CURSOR(device_id, folder_id)` for sync state

---

## Key Trade-offs

| Aspect | Choice | Trade-off |
|--------|--------|-----------|
| Chunk size | 4 MB | Smaller = more requests, larger = slower retry |
| Deduplication | Block-level | Storage savings vs. CPU overhead |
| Sync model | Event-based | Real-time feel vs. complexity |

---

## 🤖 GenAI Extension

> How could this system be augmented with LLMs? Below are interview-ready ideas that connect this classical HLD to GenAI patterns. For full GenAI system designs, see [06-genai-systems/](../../06-genai-systems/).

### Potential LLM-Powered Features

| Feature | Description | GenAI Components |
|---------|-------------|-----------------|
| **Intelligent File Search** | Semantic search across stored documents — users ask "find my tax documents from 2024" instead of browsing folders | RAG retriever (hybrid), prompt builder, LLM service |
| **Document Summarization** | Automatically generate summaries of uploaded documents (PDFs, reports) for quick preview | Chunker, prompt builder, LLM service |
| **AI File Organization** | Suggest folder structure and tags based on file content analysis | Chunker, LLM classifier |
| **Content-Based Deduplication** | Use embeddings to detect semantically similar files (not just bit-identical) for smarter dedup | Embedding service, vector DB |

### Integration Points

```
Existing File Storage Pipeline:
  Upload → Chunk → Deduplicate → Store → Sync → Download

With GenAI Extension:
  Upload → Chunk → Deduplicate → Store → Sync
              │
              └→ Async: Extract text → Embed → Index in vector DB
              └→ Async: Summarize (LLM) → Store summary metadata
              └→ On search: Query embedding → Retrieve → LLM answer
```

### Trade-offs

- **Indexing cost**: Embedding all files adds compute cost — index only text-based files, skip binaries and media
- **Privacy**: File contents may be sensitive — run LLMs on-premise or use private endpoints
- **Latency**: Search with LLM adds 1–2s — use semantic caching for repeated queries

### Learn More

- [GenAI HLD Projects: RAG-Based Enterprise Search](../../06-genai-systems/02-llm-hld-projects/) — RAG search applicable to file storage
- [GenAI LLD: Chunker & Metadata Indexer](../../06-genai-systems/01-llm-lld-projects/chunker-metadata-indexer/) — Document chunking for indexing
- [GenAI Concepts: RAG Architecture](../../06-genai-systems/00-concepts/rag-architecture/) — Retrieval-augmented generation patterns


## Bottlenecks and Failure Modes

| Component | Failure Mode | Mitigation | Impact | Detection | Recovery |
|---|---|---|---|---|---|
| Block Service | CPU Bottleneck | Horizontal scaling | Slower uploads/downloads | CPU utilization alarm | Auto-scale |
| Object Storage | AZ Outage | Cross-region replication | Degraded performance or read-only | Error rate spike | Failover to healthy AZ |
| Metadata DB | Primary Failure | Synchronous replica | Brief write unavailability | Connection timeouts | Promote replica |
| API Gateway | Instance Crash | Auto-scaling group, LB health checks | Brief latency spike for some users | 5xx rate spikes | Auto-replace |
| Sync Worker | Network Partition | Retry with exponential backoff | Out of date local files | Sync error logs | Self-healing on reconnect |
| Redis Cache | Node Failure | Redis Cluster with replicas | Cache misses hit DB | Replication lag alarm | Auto-promote replica |

## Scaling Stages

- **10K Users**: Single monolith, simple DB, basic caching.
- **1M Users**: Microservices, robust cache, read replicas.
- **100M+ Users**: Sharded databases, globally distributed edge nodes, event streaming.


---
**Real-world reference**: See how Amazon solved this in the [Amazon case study](../../case-studies/amazon-orders/)
