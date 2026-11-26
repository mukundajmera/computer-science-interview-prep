# Comparisons

## Pre-filtering vs Post-filtering ACLs
*   **Pre-filtering (In-Engine):** Applies ACLs *during* the graph traversal (HNSW). This maintains high recall. Performance can degrade if the filter matches a very small percentage of the dataset.
*   **Post-filtering:** Retrieves top K docs using ANN, then filters out docs the user cannot see. If a user is highly restricted, all K docs might be filtered out, resulting in a recall cliff.

## Multi-Tenancy Strategy
*   **Index-per-Tenant:** Maximum isolation, but difficult to scale to 1,000 tenants without massive overhead.
*   **Shared Index with TenantID Filtering:** Highly scalable. TenantID is simply another metadata filter applied at query time. We choose this approach for 1,000 tenants.

### Standardized Schema for ACLs
To enforce single-stage pre-retrieval ACL filtering, documents must adhere to a standardized schema:

**Java:**
```java
import java.util.List;

public class DocumentSchema {
    public final String id;
    public final String content;
    public final String tenantId;
    public final List<String> aclList;

    public DocumentSchema(String id, String content, String tenantId, List<String> aclList) {
        this.id = id;
        this.content = content;
        this.tenantId = tenantId;
        this.aclList = aclList;
    }
}
```

**Python:**
```python
from dataclasses import dataclass
from typing import List

@dataclass
class DocumentSchema:
    id: str
    content: str
    tenant_id: str
    acl_list: List[str]
```

## Retrieval Alternatives
*   **Hybrid Search vs Dense Vectors Only:** Hybrid search (BM25 + Dense) provides robust retrieval for both exact keyword matches (IDs, product names, acronyms) and semantic meaning. Dense vectors alone struggle with specific technical terminology, leading to lower recall on enterprise data where precise terminology matters.
*   **Cross-Encoder Reranking vs LLM-as-a-Judge:** Cross-encoders are much faster (often <100ms) and cheaper, making them suitable for real-time retrieval SLAs (p95 < 500ms). LLM-as-a-Judge (prompting a large model to rank documents) is far too slow and expensive for inline reranking but is useful for offline evaluation pipelines.
