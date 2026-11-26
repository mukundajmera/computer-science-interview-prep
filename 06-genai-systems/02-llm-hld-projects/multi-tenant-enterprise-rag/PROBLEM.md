# Multi-Tenant Enterprise RAG

## Problem Statement

Design a multi-tenant enterprise Retrieval-Augmented Generation (RAG) system. The system needs to support 1,000 enterprise tenants, storing 100M documents ingested from sources like Confluence, Google Drive, Jira, and S3. 

### Core Requirements
*   **Scale:** 1,000 enterprise tenants.
*   **Data Volume:** 100M documents across various data sources (Confluence, Google Drive, Jira, S3). Note: The 100M documents target is a scenario assumption with a budget, not benchmark evidence.
*   **Security:** Cross-tenant, strict user-level RBAC/ABAC ACL permissions must be enforced at retrieval time. Revocation and retrieval guarantees must be explicitly stated for each stage (Ingestion, Processing, Retrieval, Filtering).
*   **Latency:** Sub-500ms retrieval p95 SLA. Note: The p95 SLA target is a scenario assumption with a budget, not benchmark evidence.

### System Components
*   **Ingestion:** Document ingestion with CDC (Change Data Capture) connectors.
*   **Processing:** Chunking with ACL metadata inheritance.
*   **Retrieval:** Hybrid retrieval (dense embeddings + BM25 keyword search) aggregated via Reciprocal Rank Fusion (RRF).
*   **Filtering:** Single-stage in-engine ACL filtering to avoid post-filter recall cliffs.
*   **Reranking:** Cross-encoder reranking.
