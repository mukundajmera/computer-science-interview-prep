# RAG and Vector DB Quiz - Answer Key

## Answers

1. **D** - Recursive character splitting with sentence boundary awareness

**Explanation:**
Recursive character splitting allows the chunker to break down text recursively based on a list of separators (e.g., double newline, newline, space), ensuring that semantic units like paragraphs or sentences remain intact. Fixed-size chunking risks cutting sentences in half. Token-based chunking without semantic boundary awareness also breaks sentences. Byte-level is highly likely to cut off words or Unicode characters.

**Boundary/Misconception:**
It is essential to distinguish this from distractors like "Byte-level chunking at every 1024 bytes" or "Fixed-size chunking of 512 tokens with 0 overlap".

2. **C** - IVF-PQ (Inverted File with Product Quantization)

**Explanation:**
IVF-PQ (Inverted File with Product Quantization) significantly reduces the memory footprint required to store embeddings by dividing vectors into sub-vectors and representing them using cluster centroids (quantization), while the inverted file (IVF) narrows the search space. This makes it ideal for billion-scale datasets where exact k-NN or unquantized HNSW would exceed memory limits.

**Boundary/Misconception:**
It is essential to distinguish this from distractors like "HNSW without quantization," which offers extremely fast latency but requires a massive memory overhead to store the raw vectors and graph connections, making it unsuitable for strict memory constraints at a billion-scale.

3. **C** - Hybrid search combining sparse (BM25) and dense embeddings, followed by a cross-encoder re-ranking step

**Explanation:**
Hybrid search leverages both sparse retrieval (BM25), which excels at exact keyword matching, and dense retrieval, which captures semantic meaning. By combining both methods to form an initial pool and applying a cross-encoder, the pipeline maximizes both recall and precision.

**Boundary/Misconception:**
It is essential to distinguish this from distractors like pure dense retrieval, which fails on acronyms, or pure sparse, which lacks semantics.

4. **C** - Utilizing namespace-level or collection-level isolation within a single shared cluster

**Explanation:**
Using namespace-level or collection-level isolation within a single shared Vector DB cluster provides a strong logical boundary between tenants (preventing cross-tenant leakage by the database engine itself) without the prohibitive operational cost and resource waste of provisioning dedicated physical clusters for every tenant. Metadata filtering (A) is prone to application-layer bugs leaking data, while dedicated clusters (B) do not scale operationally for thousands of tenants.

**Boundary/Misconception:**
It is essential to distinguish this from distractors like "Storing all tenants in a single global index with metadata filtering applied at query time", which offers weak isolation, or "Creating a separate dedicated physical index cluster for each individual tenant", which fails operationally at scale.
