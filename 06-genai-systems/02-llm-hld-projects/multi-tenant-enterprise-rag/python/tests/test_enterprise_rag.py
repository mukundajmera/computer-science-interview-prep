import unittest
import importlib.util
import sys

# Dynamically import the target module
spec = importlib.util.spec_from_file_location(
    "enterprise_rag", 
    "06-genai-systems/02-llm-hld-projects/multi-tenant-enterprise-rag/python/v1-basic/enterprise_rag.py"
)
enterprise_rag = importlib.util.module_from_spec(spec)
sys.modules["enterprise_rag"] = enterprise_rag
spec.loader.exec_module(enterprise_rag)

class TestEnterpriseRAG(unittest.TestCase):
    def setUp(self):
        self.engine = enterprise_rag.EnterpriseRAGEngine()
        
        # Tenant 1 Docs
        self.engine.ingest(enterprise_rag.DocumentChunk("doc1", "t1", "Public info", ["group:all"]))
        self.engine.ingest(enterprise_rag.DocumentChunk("doc2", "t1", "Engineering secrets", ["group:eng"]))
        self.engine.ingest(enterprise_rag.DocumentChunk("doc3", "t1", "HR files", ["group:hr"]))
        
        # Tenant 2 Docs
        self.engine.ingest(enterprise_rag.DocumentChunk("doc4", "t2", "Marketing plan", ["group:mkt"]))

    def test_tenant_isolation(self):
        # User in t2 should not see t1 docs, even if they have group:all (assuming roles are tenant-scoped in practice, but here tenant isolation is primary)
        results = self.engine.retrieve("query", "t2", ["group:all"])
        self.assertEqual(len(results), 0)
        
        results = self.engine.retrieve("query", "t2", ["group:mkt"])
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].chunk_id, "doc4")

    def test_acl_enforcement(self):
        # User with only group:all
        results = self.engine.retrieve("query", "t1", ["group:all"])
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].chunk_id, "doc1")
        
        # User with eng and all
        results = self.engine.retrieve("query", "t1", ["group:all", "group:eng"])
        self.assertEqual(len(results), 2)
        chunk_ids = [doc.chunk_id for doc in results]
        self.assertIn("doc1", chunk_ids)
        self.assertIn("doc2", chunk_ids)
        
        # Admin with all groups
        results = self.engine.retrieve("query", "t1", ["group:all", "group:eng", "group:hr"])
        self.assertEqual(len(results), 3)

    def test_no_access(self):
        # User with irrelevant group
        results = self.engine.retrieve("query", "t1", ["group:sales"])
        self.assertEqual(len(results), 0)

    def test_revoked_permissions(self):
        # Update existing doc to revoke permissions for group:eng
        self.engine.ingest(enterprise_rag.DocumentChunk("doc2", "t1", "Engineering secrets", ["group:admin"]))
        
        # User with group:eng should no longer have access
        results = self.engine.retrieve("query", "t1", ["group:eng"])
        self.assertEqual(len(results), 0)

        # Admin user should still have access
        results = self.engine.retrieve("query", "t1", ["group:admin"])
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].chunk_id, "doc2")

    def test_deleted_chunks(self):
        # User with group:hr has access initially
        results = self.engine.retrieve("query", "t1", ["group:hr"])
        self.assertEqual(len(results), 1)

        # Update doc to be deleted
        deleted_doc = enterprise_rag.DocumentChunk("doc3", "t1", "HR files", ["group:hr"])
        deleted_doc.is_deleted = True
        self.engine.ingest(deleted_doc)

        # User with group:hr should not have access to deleted chunk
        results = self.engine.retrieve("query", "t1", ["group:hr"])
        self.assertEqual(len(results), 0)

    def test_duplicate_ids(self):
        # Add doc with id "doc1" for tenant "t2"
        self.engine.ingest(enterprise_rag.DocumentChunk("doc1", "t2", "Marketing secrets", ["group:mkt"]))

        # Check tenant 1 can still access its "doc1"
        results_t1 = self.engine.retrieve("query", "t1", ["group:all"])
        self.assertEqual(len(results_t1), 1)
        self.assertEqual(results_t1[0].tenant_id, "t1")

        # Check tenant 2 can access its "doc1"
        results_t2 = self.engine.retrieve("query", "t2", ["group:mkt"])
        # Should return both doc4 and doc1
        self.assertEqual(len(results_t2), 2)
        chunk_ids = [doc.chunk_id for doc in results_t2]
        self.assertIn("doc1", chunk_ids)
        self.assertIn("doc4", chunk_ids)
        # Verify isolation
        is_isolated = all(doc.tenant_id == "t2" for doc in results_t2)
        self.assertTrue(is_isolated)

    def test_deterministic_ties(self):
        self.engine.ingest(enterprise_rag.DocumentChunk("doc-c", "t3", "Content C", ["group:all"]))
        self.engine.ingest(enterprise_rag.DocumentChunk("doc-a", "t3", "Content A", ["group:all"]))
        self.engine.ingest(enterprise_rag.DocumentChunk("doc-b", "t3", "Content B", ["group:all"]))

        results = self.engine.retrieve("query", "t3", ["group:all"])
        self.assertEqual(len(results), 3)

        retrieved_chunk_ids = [doc.chunk_id for doc in results]
        # Should be alphabetically sorted due to deterministic tie breaking in hybrid_search
        expected_order = ["doc-a", "doc-b", "doc-c"]
        self.assertEqual(retrieved_chunk_ids, expected_order)



    def test_empty_retrieval(self):
        # User with access to no docs should return empty list
        results = self.engine.retrieve("query", "t1", ["group:xyz"])
        self.assertEqual(len(results), 0)


if __name__ == "__main__":
    unittest.main()
