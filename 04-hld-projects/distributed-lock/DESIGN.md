# Design

Use fencing tokens for safety.

```mermaid
graph TD
    A[Client] --> B[Lock Service]
```

```mermaid
graph TD
    B --> C[Storage]
```

```mermaid
sequenceDiagram
    Client->>Lock Service: Acquire
    Lock Service-->>Client: Token 1
```
