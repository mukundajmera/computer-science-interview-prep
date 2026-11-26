import typing

class DocumentChunk:
    def __init__(self, chunk_id: str, tenant_id: str, content: str, acl_list: typing.List[str]):
        self.chunk_id = chunk_id
        self.tenant_id = tenant_id
        self.content = content
        self.acl_list = acl_list
        self.embedding: typing.Optional[typing.List[float]] = None
        self.is_deleted: bool = False

class EnterpriseRAGEngine:
    def __init__(self):
        self.documents: typing.List[DocumentChunk] = []
        
    def ingest(self, chunk: DocumentChunk) -> None:
        # Simulate embedding generation
        chunk.embedding = [0.1, 0.2, 0.3]
        
        # If a chunk with same chunk_id and tenant_id exists, replace it
        for i, existing_chunk in enumerate(self.documents):
            same_id = existing_chunk.chunk_id == chunk.chunk_id
            same_tenant = existing_chunk.tenant_id == chunk.tenant_id
            if same_id and same_tenant:
                self.documents[i] = chunk
                return
                
        self.documents.append(chunk)

    def _single_stage_acl_filter(self, docs: typing.List[DocumentChunk], tenant_id: str, user_acls: typing.List[str]) -> typing.List[DocumentChunk]:
        filtered_docs = []
        for document in docs:
            is_same_tenant = document.tenant_id == tenant_id
            if not is_same_tenant:
                continue
                
            has_access = any(acl in user_acls for acl in document.acl_list)
            if has_access:
                filtered_docs.append(document)
        return filtered_docs

    def _hybrid_search(self, docs: typing.List[DocumentChunk], query: str, top_k: int) -> typing.List[DocumentChunk]:
        # Simulate hybrid search combining dense + BM25 returning pre-filtered docs
        active_docs = [doc for doc in docs if not doc.is_deleted]
        active_docs.sort(key=lambda doc: doc.chunk_id)
        return active_docs[:top_k]

    def _reciprocal_rank_fusion(self, docs: typing.List[DocumentChunk]) -> typing.List[DocumentChunk]:
        # Simulate RRF (noop for simulation purposes, just returning the list)
        return docs

    def _cross_encoder_rerank(self, query: str, docs: typing.List[DocumentChunk]) -> typing.List[DocumentChunk]:
        # Simulate reranking (noop for simulation purposes, just returning the list)
        return docs

    def retrieve(self, query: str, tenant_id: str, user_acls: typing.List[str], top_k: int = 5) -> typing.List[DocumentChunk]:
        # 1. Single-Stage In-Engine ACL Filter (Pre-retrieval)
        filtered_docs = self._single_stage_acl_filter(self.documents, tenant_id, user_acls)
        
        # 2. Hybrid Search (Dense + BM25) on filtered docs to prevent recall cliffs
        search_results = self._hybrid_search(filtered_docs, query, top_k * 2)
        
        # 3. Reciprocal Rank Fusion
        fused_docs = self._reciprocal_rank_fusion(search_results)
        
        # 4. Cross-Encoder Reranking
        reranked_docs = self._cross_encoder_rerank(query, fused_docs)
        
        return reranked_docs[:top_k]

