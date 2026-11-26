# 🥞 Stacks & Monotonic Stack

A focus on Last-In-First-Out (LIFO) order and Monotonic stacks for bounding range queries.

---

## 📖 Overview

Stacks naturally enforce order. Monotonic Stacks specifically keep elements entirely sorted, shedding data to find the "Next Greater Element."

```mermaid
sequenceDiagram
    participant S as Stack
    participant E as Elements [2, 1, 5, 6, 2, 3]
    E->>S: Push 2 (increasing)
    E->>S: Push 1 (pop 2, area=2*1)
    Note over S: Stack state trace: [(0, 1)]
    E->>S: Push 5
    E->>S: Push 6
    Note over S: Stack state trace: [(0, 1), (2, 5), (3, 6)]
    E->>S: Push 2 (pop 6: area=6*1, pop 5: area=5*2)
```

---

## 🧭 System Design Relevance

| Problem Pattern | LLD Concept | System Design Transfer |
|---|---|---|
| Monotonic Stack | Max sliding window limiters | In-memory time series aggregations |
| Reverse Polish Notation | AST execution engines | Database query planning order |
| Parenthesis Matching | Recursive descent parsers | XML/HTML validator streams |

---
