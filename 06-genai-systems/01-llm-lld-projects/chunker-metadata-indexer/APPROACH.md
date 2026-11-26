# Design Approach for Chunker–Metadata–Indexer Pipeline

A step-by-step thought process for designing the document ingestion pipeline.

---

## Step 1: Identify Core Entities

Extract nouns from the problem statement:

| Noun | Entity? | Reasoning |
|------|---------|-----------|
| Document | ✅ Yes | Input unit carrying raw text and source info |
| Chunk | ✅ Yes | Output unit — a slice of a document |
| Chunking Strategy | ✅ Yes | Algorithm that controls how splitting happens |
| Document Chunker | ✅ Yes | Orchestrator binding a strategy to a document |
| Metadata Tag | ✅ Yes | Key-value annotation on a chunk |
| Metadata Extractor | ✅ Yes | Derives metadata from chunks |
| Index Backend | ✅ Yes | Abstract storage for chunk–embedding pairs |
| Index Entry | ✅ Yes | Single record in the index |
| Embedding | ❌ No | Opaque numeric vector — not an entity we own |
| Pipeline | 🔄 v2 | Orchestration wrapper — deferred to v2 |

**Final Entities (v1)**: Document, Chunk, ChunkingStrategy, DocumentChunker, MetadataTag, MetadataExtractor, IndexBackend, IndexEntry, InMemoryIndex

---

## Step 2: Define Relationships

```
Document (1) ──split by──> (n) Chunk
ChunkingStrategy (1) ──used by──> (1) DocumentChunker
DocumentChunker (1) ──produces──> (n) Chunk
MetadataExtractor (1) ──enriches──> (n) Chunk
Chunk (1) ──has──> (n) MetadataTag
IndexBackend (1) ──stores──> (n) IndexEntry
IndexEntry (1) ──wraps──> (1) Chunk + embedding
```

### Relationship Types:

| Relationship | Type | Description |
|--------------|------|-------------|
| Document → Chunk | Derivation | Chunks are derived from a document |
| DocumentChunker → ChunkingStrategy | Composition | Strategy injected at construction |
| Chunk → MetadataTag | Composition | Tags don't exist without their chunk |
| IndexBackend → IndexEntry | Composition | Entries belong to the index |
| IndexEntry → Chunk | Association | Entry references a chunk |

---

## Step 3: Choose Design Patterns

### Pattern Analysis:

| Pattern | Apply? | Justification |
|---------|--------|---------------|
| **Strategy** | ✅ Yes | Swap chunking algorithms without changing the orchestrator |
| **Factory** | ✅ Yes | Create index backends by name |
| **Template Method** | ✅ Yes | Base chunking flow (validate → split → assign IDs) with varying split logic |
| **Observer** | 🔄 v2 | Notify listeners on index changes |
| **Singleton** | ❌ No | No global state — prefer dependency injection |
| **Builder** | 🔄 v2 | Complex pipeline assembly in v2 |

### Pattern Application:

1. **Strategy Pattern** — ChunkingStrategy
   - `FixedSizeChunker`, `SentenceChunker`, `ParagraphChunker` implement the same interface
   - `DocumentChunker` delegates to whichever strategy is injected
   - Easy to add `TokenChunker` or `SemanticChunker` later

2. **Factory Pattern** — IndexBackend
   - A simple factory function selects among `InMemoryIndex`, and in future, `FAISSIndex`, `PineconeIndex`
   - Decouples callers from concrete backend classes

3. **Template Method** — ChunkingStrategy base class
   - Common pre/post steps (input validation, ID assignment) live in the ABC
   - Subclasses override only the `_split_text` hook

---

## Step 4: Design Classes

### Core Classes:

#### Document (dataclass)
- **Attributes**:
  - `text: str` — raw document content
  - `source: str` — origin reference (file name, URL, etc.)
  - `doc_id: str` — unique identifier (auto-generated UUID)
- **Methods**: None (pure data carrier)

#### Chunk (dataclass)
- **Attributes**:
  - `chunk_id: str` — UUID
  - `text: str` — chunk content
  - `doc_id: str` — parent document ID
  - `start_pos: int` — character offset in original document
  - `end_pos: int` — end character offset
  - `metadata: List[MetadataTag]` — attached tags
- **Methods**: None (pure data carrier)

#### ChunkingStrategy (ABC)
- **Methods**:
  - `chunk(document: Document) → List[Chunk]` — public entry point (template method)
  - `_split_text(text: str) → List[Tuple[str, int, int]]` — abstract hook
- **Implementations**: FixedSizeChunker, SentenceChunker, ParagraphChunker

#### FixedSizeChunker
- **Attributes**:
  - `chunk_size: int` — max characters per chunk
  - `overlap: int` — character overlap between consecutive chunks
- **Split logic**: Slide a window of `chunk_size` with step `chunk_size - overlap`

#### SentenceChunker
- **Attributes**:
  - `max_sentences: int` — sentences per chunk
  - `overlap: int` — sentence overlap
- **Split logic**: Detect sentence boundaries, group into chunks

#### ParagraphChunker
- **Attributes**: None beyond base
- **Split logic**: Split on double-newline (`\n\n`) boundaries

#### DocumentChunker
- **Attributes**:
  - `strategy: ChunkingStrategy` — injected strategy
- **Methods**:
  - `chunk(document: Document) → List[Chunk]` — delegates to strategy

#### MetadataTag (dataclass)
- **Attributes**:
  - `key: str`
  - `value: str`

#### MetadataExtractor
- **Methods**:
  - `extract(chunks: List[Chunk], document: Document) → List[Chunk]` — enriches chunks in-place

#### IndexBackend (ABC)
- **Methods**:
  - `add(chunk: Chunk, embedding: List[float]) → None`
  - `search(query_embedding: List[float], top_k: int) → List[IndexEntry]`
  - `delete(chunk_id: str) → bool`
  - `size() → int`

#### InMemoryIndex (IndexBackend)
- **Attributes**:
  - `_entries: Dict[str, IndexEntry]` — chunk_id → entry
- **Search**: Brute-force cosine similarity

#### IndexEntry (dataclass)
- **Attributes**:
  - `chunk: Chunk`
  - `embedding: List[float]`
  - `score: float` — populated during search results

---

## Step 5: Handle Edge Cases

### Input Validation:
- Empty or whitespace-only document text
- `chunk_size` ≤ 0 or `overlap` ≥ `chunk_size`
- Negative `top_k` in search
- Empty embedding vector or dimension mismatch

### Business Logic:
- Document shorter than chunk size → single chunk
- No sentences detected → fall back to single chunk
- No paragraphs detected → treat entire text as one paragraph
- Duplicate chunk IDs (prevented by UUID)
- Search on empty index → return empty list
- Delete non-existent chunk → return False

### Boundary Conditions:
- Overlap of zero (no overlap)
- Very large documents (performance should remain linear)
- Unicode text with multi-byte characters
- Trailing whitespace / newlines in document

---

## Step 6: Optimization Opportunities

### Data Structures:

| Operation | v1 Basic | v3 Optimized |
|-----------|----------|--------------|
| Chunk a document | O(n) | O(n) |
| Metadata extraction | O(n) | O(n) |
| Index add | O(1) | O(1) |
| Index search | O(k) brute-force | O(log k) ANN |
| Index delete | O(1) | O(1) |

*n = document length in characters, k = number of indexed entries*

### Caching:
- Cache embeddings by chunk content hash to avoid re-computing
- Pre-compute and store norms for cosine similarity

### Indexing:
- `Dict[str, IndexEntry]` — O(1) lookup/delete by chunk_id
- Sorted structures or KD-trees for approximate nearest neighbor (v3)

---

## Step 7: Version Progression

### v1-basic
- Three chunking strategies (fixed, sentence, paragraph)
- Metadata extractor with standard tags
- In-memory index with brute-force cosine search
- No concurrency, no persistence

### v2-extended
- Token-aware chunking (simulated token counts)
- Filtered search by metadata tag
- Batch add/delete on index
- Pipeline orchestrator class

### v3-optimized
- ANN index stub (locality-sensitive hashing)
- Async pipeline with `asyncio`
- Embedding cache with LRU eviction
- Persistence adapter (JSON file-backed)

---

## Code Organization

```
chunker-metadata-indexer/
├── PROBLEM.md                  # Requirements and constraints
├── APPROACH.md                 # This design walkthrough
├── DESIGN.md                   # Class diagrams and decisions
├── python/
│   ├── v1-basic/
│   │   ├── __init__.py         # Package marker
│   │   ├── chunker.py          # Document, Chunk, strategies, DocumentChunker
│   │   ├── metadata.py         # MetadataTag, MetadataExtractor
│   │   ├── index.py            # IndexBackend ABC, InMemoryIndex, IndexEntry
│   │   └── demo.py             # Runnable end-to-end example
│   └── tests/
│       ├── __init__.py         # Package marker
│       └── test_chunker.py     # Unit tests for all components
```

---

## Interview Discussion Points

1. **Why Strategy for Chunking?**
   - Different retrieval tasks need different chunk granularities
   - Callers swap strategies without touching orchestration code
   - Follows Open/Closed Principle — add a `SemanticChunker` tomorrow

2. **Why an ABC for IndexBackend?**
   - Production systems use FAISS, Pinecone, Weaviate, etc.
   - A clean interface lets us develop business logic against the abstraction
   - In-memory backend keeps tests fast and dependency-free

3. **Why not generate real embeddings?**
   - Embedding generation is an infrastructure concern, not a design concern
   - Keeping it as `List[float]` lets us focus on the pipeline design
   - Callers can plug in any model (OpenAI, Sentence-Transformers, etc.)

4. **How would you add persistence?**
   - Implement a new `IndexBackend` subclass (e.g., `SQLiteIndex`)
   - Serialize `IndexEntry` on `add`, deserialize on `search`
   - No changes to chunking or metadata code
