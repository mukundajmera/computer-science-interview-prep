# Code Walkthrough: Dynamic Feature Flag Engine

## Entry APIs
The primary entry point is `ConfigEngine` with two main methods:
- `update_flag(flag: FeatureFlag) -> None` (Python) / `updateFlag(FeatureFlag flag)` (Java)
- `evaluate(flag_key: str, context: UserContext) -> Variant` (Python) / `evaluate(String flagKey, UserContext context)` (Java)
- `register_listener(flag_key: str, listener: Callable)` (Python) / `registerListener(String flagKey, ConfigListener listener)` (Java) (v3 only)

## Version Delta Table

| Version | Focus | Core Mechanics | Complexity (Time/Space) |
|---|---|---|---|
| **v1-basic** | Simple boolean flags | Flat key-value map for direct lookups. | Read: $O(1)$ Time / Space: $O(F)$ where F is flag count |
| **v2-extended** | Multi-variant & rules | `FeatureFlag` -> list of `Rule`s evaluating `UserContext` | Read: $O(R)$ Time where R is rules per flag / Space: $O(F \times R)$ |
| **v3-optimized** | Rollouts & Listeners | Deterministic hashing (MD5 modulo 100 via `hashlib`/`MessageDigest`). Observer pattern with `RLock`/`ConcurrentHashMap`. | Read: $O(R)$ Time / Space: $O(F \times R + L)$ where L is listener count |

## Detailed Progression

### v1-basic
- **Focus**: Basic boolean flags and user attributes.
- **Implementation**: Simple map of flag keys to boolean values.
- **Testing**: Tests cover basic retrieval and defaults.

### v2-extended
- **Focus**: Multi-variant flags and segment targeting.
- **Implementation**: Introduces `FeatureFlag`, `Rule`, and `Variant` classes. Rule engine evaluates `UserContext` attributes (e.g., country == "US").
- **Testing**: Tests cover segment matching and multi-variant evaluation.

### v3-optimized
- **Focus**: Percentage rollouts, change listeners, and concurrency.
- **Implementation**: 
  - Adds deterministic hashing (MD5 hash modulo 100) for rollouts.
  - Implements the Observer pattern for config changes.
  - Uses `ConcurrentHashMap` (Java) / `threading.RLock` (Python) and thread-safe data structures for updates and evaluations.
- **Testing**: Validates hashing determinism, concurrent evaluation, and listener execution.
