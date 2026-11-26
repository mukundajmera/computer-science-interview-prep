# Grading Rubric

## Expected Signals
*   **Scale:** Must explicitly handle 1,000 tenants and 100M docs (typically via shared index with tenant routing). Stated scale and latency targets must be treated as budget assumptions for capacity planning, not mere benchmarks.
*   **Security:** ACL enforced correctly (single-stage pre-filtering is a must). Must explicitly guarantee cross-tenant isolation and revocation boundaries at every pipeline stage.
*   **Latency:** Explains how to meet the p95 < 500ms (caching, limited reranking scope).
*   **Retrieval:** Mentions BM25 + Vector + RRF + Cross-Encoder. Must explicitly aggregate dense/keyword scores via RRF for deterministic top-k ordering.
*   **Evaluation:** Distinguishes ACL safety from search relevance by defining independent evaluation criteria (e.g., zero false-positives for unauthorized doc retrieval vs. high nDCG for authorized retrieval).
*   **Performance Verification:** Distinguishes offline fixture success (simulations or proof sketches) from production-scale p95 evidence, explicitly acknowledging that simulations cannot validate production latency limits at the 100M document scale.

### Offline Fixture for ACL Safety
**Java:**
```java
import java.util.List;

public class AclSafetyFixture {
    public void testAclSafety() {
        DocumentSchema secretDoc = new DocumentSchema("doc1", "Secret", "tenantA", List.of("user_123"));
        String searchUserId = "user_999"; // Unauthorized user
        boolean hasAccess = secretDoc.aclList.contains(searchUserId);
        if (hasAccess) {
            throw new AssertionError("Unauthorized access allowed!");
        }
    }
}
```

**Python:**
```python
def test_acl_safety():
    secret_doc = DocumentSchema(id="doc1", content="Secret", tenant_id="tenantA", acl_list=["user_123"])
    search_user_id = "user_999"  # Unauthorized user
    has_access = search_user_id in secret_doc.acl_list
    assert not has_access, "Unauthorized access allowed!"
```
