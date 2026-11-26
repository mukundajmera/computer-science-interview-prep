# Context Window Manager - Approach

## Context Assembly Strategy

The core challenge of prompt assembly is satisfying multiple constraints: token budget limits, semantic completeness, and attention mechanics. Our approach utilizes a multi-phase orchestration pipeline to resolve these constraints gracefully.

### 1. The Token Estimation Fallback

Since we operate in an offline, standard-library restricted sandbox (to simulate isolation), we do not integrate real tokenizers like `tiktoken`. Instead, we define a strict interface:
`TokenizerInterface.estimate_tokens(text: str) -> int`.
Our fallback implementation approximates tokens by counting whitespace-delimited words and applying a standard `1 word = 1.3 tokens` multiplier. While not completely precise, it guarantees the mathematical determinism necessary for reliable unit testing and budget truncation logic.

### 2. Priority-Based Eviction Pipeline

Segments are added to the manager with a predefined priority (1-5). During compilation, the system follows a deterministic loop:
- Calculate total tokens.
- If total > budget, identify the lowest-priority category currently holding context.
- Within that category (e.g., Priority 5 - Chat History), apply a sliding window mechanism. We iteratively remove the oldest message (or the least relevant RAG chunk) and recalculate.
- If an entire priority tier is exhausted and we remain over budget, the system escalates eviction to the next lowest tier.
- If Priority 1 and 2 segments combined exceed the entire budget, the system raises a specific `ContextOverflowError`.

### 3. The Lost-in-the-Middle Reordering Algorithm

LLMs are prone to the "lost-in-the-middle" effect, where attention weights decay for information located deep within the prompt body. Our assembly strategy specifically reorders final segments right before serialization:
- The Absolute Highest Priority (System Prompt) is anchored to the beginning (Index 0).
- The Second Highest Priority (Current User Query) is anchored to the very end (Index -1).
- The remaining segments (Tools, RAG context, Chat History) are interleaved in the middle. Tools are generally placed closer to the top, while recent chat history remains closer to the query. 
This exact positional guarantee ensures that regardless of how much RAG context is included, the core query and safety rules remain the most heavily attended tokens.

### 4. Summarization / Compaction Hooks

To prevent the user from experiencing a sudden, total loss of conversation history due to truncation, the manager exposes a summarization hook. When Priority 5 (Chat History) crosses a configured "soft limit" percentage of the total budget, the system can emit a compaction request. The calling application uses this to invoke an external LLM call that replaces older messages with a dense summary, which is then re-injected as a single block in subsequent turns.

### 5. Cancellation / Interrupt

To support early cancellation in highly concurrent or latency-sensitive environments, the manager exposes a `cancel()` method. If called, it sets an internal flag (`_is_cancelled`). The `compile()` and eviction loops must check this flag and safely abort mid-flight operations.

---

## Explicit Reference Contracts

To demonstrate full logic parity and model/provider independence, the implementation is mirrored across Java and Python. Below are the reference contracts.

### Python Reference Implementation

```python
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import List

class Priority(Enum):
    SYSTEM = 1
    USER_QUERY = 2
    TOOL_DEF = 3
    RAG_CONTEXT = 4
    HISTORY = 5

class TokenizerInterface(ABC):
    @abstractmethod
    def estimate_tokens(self, text: str) -> int:
        pass

class ContextOverflowError(Exception):
    pass

@dataclass
class ContextSegment:
    id: str
    text: str
    priority: Priority
    token_count: int

class ContextWindowManager:
    def __init__(self, total_budget: int, soft_limit_ratio: float = 0.8, tokenizer: TokenizerInterface = None):
        pass

    def add_segment(self, text: str, priority: Priority, id: str) -> None:
        pass

    def requires_summarization(self) -> bool:
        pass

    def _evict_to_fit(self) -> List[ContextSegment]:
        pass
        
    def _reorder_for_attention(self, remaining: List[ContextSegment]) -> List[ContextSegment]:
        pass

    def compile(self) -> List[str]:
        pass

    def cancel(self) -> None:
        pass
```

### Java Reference Implementation

```java
import java.util.List;

public enum Priority {
    SYSTEM(1),
    USER_QUERY(2),
    TOOL_DEF(3),
    RAG_CONTEXT(4),
    HISTORY(5);

    private final int level;

    Priority(int level) {
        this.level = level;
    }
    
    public int getLevel() { return level; }
}

public interface TokenizerInterface {
    int estimateTokens(String text);
}

public class ContextOverflowException extends RuntimeException {
    public ContextOverflowException(String message) {
        super(message);
    }
}

public class ContextSegment {
    private String id;
    private String text;
    private Priority priority;
    private int tokenCount;
    
    // Constructors, Getters, Setters
}

public class ContextWindowManager {
    public ContextWindowManager(int totalBudget, double softLimitRatio, TokenizerInterface tokenizer) {
        // ...
    }

    public void addSegment(String text, Priority priority, String id) {
        // ...
    }

    public boolean requiresSummarization() {
        // ...
        return false;
    }
    
    private List<ContextSegment> evictToFit() {
        // ...
        return null;
    }

    public void cancel() {
        // ...
    }

    private List<ContextSegment> reorderForAttention(List<ContextSegment> remaining) {
        // ...
        return null;
    }

    public List<String> compile() {
        // ...
        return null;
    }
}
```

---

## Trade-Offs

- **Approximation vs Accuracy**: Relying on a word-based multiplier for token estimation is inaccurate for code, non-Latin languages, or highly symbol-dense text. However, by strictly typing the interface, production applications simply inject an accurate exact tokenizer.
- **Strict Categorization**: Fixed priority buckets (1 through 5) may be too rigid for complex agents that dynamically value RAG context over older user queries. A more advanced approach could use dynamic scoring, but the rigid tiers make debugging, verification, and latency highly predictable.
