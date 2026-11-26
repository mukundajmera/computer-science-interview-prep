import math
import re
from typing import List, Dict, Any, Tuple
from dataclasses import dataclass
from collections import defaultdict

@dataclass
class Chunk:
    id: str
    text: str
    metadata: Dict[str, Any]
    vector: List[float] = None

class DocumentProcessor:
    def __init__(self, chunk_size: int = 512, overlap: int = 64):
        self.chunk_size = chunk_size
        self.overlap = overlap

    def chunk_document(self, doc_id: str, text: str, metadata: Dict[str, Any] = None) -> List[Chunk]:
        """
        Sliding-window chunking based on word tokens (simplified for standard library).
        """
        if metadata is None:
            metadata = {}

        words = text.split()
        chunks = []
        chunk_idx = 0

        if not words:
            return chunks

        i = 0
        while i < len(words):
            chunk_words = words[i:i + self.chunk_size]
            chunk_text = " ".join(chunk_words)

            chunk_metadata = metadata.copy()
            chunk_metadata["doc_id"] = doc_id
            chunk_metadata["chunk_index"] = chunk_idx

            chunks.append(Chunk(
                id=f"{doc_id}_{chunk_idx}",
                text=chunk_text,
                metadata=chunk_metadata
            ))

            chunk_idx += 1
            if i + self.chunk_size >= len(words):
                break
            i += (self.chunk_size - self.overlap)

        return chunks

class SimulatedEmbeddings:
    @staticmethod
    def get_embedding(text: str) -> List[float]:
        # Simple simulated embedding for demonstration (using character frequencies as a naive vector)
        vec = [0.0] * 26
        text_lower = text.lower()
        for char in text_lower:
            if 'a' <= char <= 'z':
                vec[ord(char) - ord('a')] += 1.0

        # Normalize
        norm = math.sqrt(sum(v * v for v in vec))
        if norm > 0:
            vec = [v / norm for v in vec]
        return vec

def cosine_similarity(v1: List[float], v2: List[float]) -> float:
    if not v1 or not v2:
        return 0.0
    dot = sum(a * b for a, b in zip(v1, v2))
    return dot

class KeywordBM25Sim:
    def __init__(self):
        self.doc_freqs = defaultdict(int)
        self.doc_lengths = {}
        self.doc_term_freqs = {}
        self.avg_doc_len = 0
        self.total_docs = 0
        self.k1 = 1.5
        self.b = 0.75

    def add_chunk(self, chunk: Chunk):
        terms = self._tokenize(chunk.text)
        self.total_docs += 1
        self.doc_lengths[chunk.id] = len(terms)

        term_freqs = defaultdict(int)
        for term in terms:
            term_freqs[term] += 1

        self.doc_term_freqs[chunk.id] = term_freqs

        for term in set(terms):
            self.doc_freqs[term] += 1

        self.avg_doc_len = sum(self.doc_lengths.values()) / self.total_docs

    def _tokenize(self, text: str) -> List[str]:
        return re.findall(r'\w+', text.lower())

    def search(self, query: str) -> Dict[str, float]:
        terms = self._tokenize(query)
        scores = defaultdict(float)

        for term in terms:
            if term not in self.doc_freqs:
                continue

            idf = math.log((self.total_docs - self.doc_freqs[term] + 0.5) /
                          (self.doc_freqs[term] + 0.5) + 1.0)

            for doc_id, tfs in self.doc_term_freqs.items():
                if term in tfs:
                    tf = tfs[term]
                    doc_len = self.doc_lengths[doc_id]

                    numerator = tf * (self.k1 + 1)
                    # Handle case where avg_doc_len might be 0, though unlikely with total_docs > 0
                    denominator = tf + self.k1 * (1 - self.b + self.b * (doc_len / (self.avg_doc_len or 1)))

                    scores[doc_id] += idf * (numerator / denominator)

        return scores

class VectorDB:
    def __init__(self):
        self.chunks = {}

    def add_chunk(self, chunk: Chunk):
        if not chunk.vector:
            chunk.vector = SimulatedEmbeddings.get_embedding(chunk.text)
        self.chunks[chunk.id] = chunk

    def search(self, query_vector: List[float]) -> Dict[str, float]:
        scores = {}
        for chunk_id, chunk in self.chunks.items():
            scores[chunk_id] = cosine_similarity(query_vector, chunk.vector)
        return scores

class HybridRetriever:
    def __init__(self):
        self.keyword_db = KeywordBM25Sim()
        self.vector_db = VectorDB()
        self.chunks_map = {}

    def ingest(self, chunk: Chunk):
        self.chunks_map[chunk.id] = chunk
        self.keyword_db.add_chunk(chunk)
        self.vector_db.add_chunk(chunk)

    def reciprocal_rank_fusion(self, vector_results: List[Tuple[str, float]],
                              keyword_results: List[Tuple[str, float]],
                              k: int = 60) -> List[Tuple[str, float]]:
        """
        RRF algorithm for hybrid search scoring.
        score = 1 / (k + rank)
        """
        rrf_scores = defaultdict(float)

        for rank, (doc_id, _) in enumerate(vector_results, 1):
            rrf_scores[doc_id] += 1.0 / (k + rank)

        for rank, (doc_id, _) in enumerate(keyword_results, 1):
            rrf_scores[doc_id] += 1.0 / (k + rank)

        return sorted(rrf_scores.items(), key=lambda x: x[1], reverse=True)

    def search(self, query: str, top_k: int = 5) -> List[Chunk]:
        # Keyword Search
        keyword_scores = self.keyword_db.search(query)
        kw_sorted = sorted(keyword_scores.items(), key=lambda x: x[1], reverse=True)

        # Vector Search
        query_vec = SimulatedEmbeddings.get_embedding(query)
        vector_scores = self.vector_db.search(query_vec)
        vec_sorted = sorted(vector_scores.items(), key=lambda x: x[1], reverse=True)

        # Reciprocal Rank Fusion
        fused_results = self.reciprocal_rank_fusion(vec_sorted, kw_sorted)

        # Return Top K Chunks
        top_chunks = []
        for chunk_id, _ in fused_results[:top_k]:
            top_chunks.append(self.chunks_map[chunk_id])

        return top_chunks

class PromptBuilder:
    def __init__(self, max_context_tokens: int = 1000):
        self.max_context_tokens = max_context_tokens

    def build_prompt(self, query: str, retrieved_chunks: List[Chunk]) -> str:
        """
        Builds the prompt with context window truncation and citation attribution.
        Uses a naive word count as a token proxy for standard lib compatibility.
        """
        system_prompt = "You are a helpful assistant. Use the following context to answer the question. Cite your sources using [Source N].\n"

        current_tokens = len(system_prompt.split()) + len(query.split()) + 20 # Buffer
        context_parts = []

        for i, chunk in enumerate(retrieved_chunks, 1):
            doc_title = chunk.metadata.get('doc_title', 'Unknown Document')
            page_num = chunk.metadata.get('page_num', 'Unknown')
            citation = f"[Source {i}] {doc_title} - Page {page_num}:\n{chunk.text}\n"
            citation_tokens = len(citation.split())

            if current_tokens + citation_tokens > self.max_context_tokens:
                break # Truncate context window

            context_parts.append(citation)
            current_tokens += citation_tokens

        context_str = "\n".join(context_parts)

        prompt = f"{system_prompt}\nCONTEXT:\n{context_str}\nQUESTION: {query}\nANSWER:"
        return prompt

class RAGPipeline:
    def __init__(self, chunk_size: int = 512, overlap: int = 64, max_context_tokens: int = 1000):
        self.processor = DocumentProcessor(chunk_size=chunk_size, overlap=overlap)
        self.retriever = HybridRetriever()
        self.prompt_builder = PromptBuilder(max_context_tokens=max_context_tokens)

    def ingest_document(self, doc_id: str, text: str, metadata: Dict[str, Any] = None):
        chunks = self.processor.chunk_document(doc_id, text, metadata)
        for chunk in chunks:
            self.retriever.ingest(chunk)

    def query(self, user_query: str, top_k: int = 3) -> str:
        top_chunks = self.retriever.search(user_query, top_k=top_k)
        prompt = self.prompt_builder.build_prompt(user_query, top_chunks)
        return prompt
