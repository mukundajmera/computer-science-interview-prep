# Design Pattern Completion Matrix

This matrix makes the repository's design-pattern coverage explicit. A pattern can be useful for learners with theory and dual-language `v1-basic` examples, but that is not the same as full `v1/v2/v3` progression or executable tests. Matrix Yes fields assert structural coverage and existence, not semantically correct or behaviorally executed tests. No claim of all 23 patterns being semantically correct is inferred from current matrix Yes fields. Use the opt-in evidence modes to see executed behavior evidence.

Coverage terms:

- **Theory:** pattern `README.md` exists.
- **Java v1 / Python v1:** `v1-basic` implementation exists with source files.
- **Java tests / Python tests:** language-specific test directory exists with test source files.
- **v2/v3 progression:** full progressive implementation track exists when both Java and Python have source-backed `v2-*` and `v3-*` folders. Existing repo naming includes `v2-variant`, `v2-pythonic`, and `v3-advanced`. `Planned` means no v2/v3 source exists yet.

## Current Coverage

| Pattern | Category | Theory | Java v1 | Python v1 | Java tests | Python tests | v2/v3 progression |
|---------|----------|--------|---------|-----------|------------|--------------|-------------------|
| [Abstract Factory](./creational/abstract-factory/) | Creational | Yes | Yes | Yes | Yes | Yes | Yes |
| [Builder](./creational/builder/) | Creational | Yes | Yes | Yes | Yes | Yes | Yes |
| [Factory Method](./creational/factory-method/) | Creational | Yes | Yes | Yes | Yes | Yes | Yes |
| [Prototype](./creational/prototype/) | Creational | Yes | Yes | Yes | Yes | Yes | Yes |
| [Singleton](./creational/singleton/) | Creational | Yes | Yes | Yes | Yes | Yes | Yes |
| [Adapter](./structural/adapter/) | Structural | Yes | Yes | Yes | Yes | Yes | Yes |
| [Bridge](./structural/bridge/) | Structural | Yes | Yes | Yes | Yes | Yes | Yes |
| [Composite](./structural/composite/) | Structural | Yes | Yes | Yes | Yes | Yes | Yes |
| [Decorator](./structural/decorator/) | Structural | Yes | Yes | Yes | Yes | Yes | Yes |
| [Facade](./structural/facade/) | Structural | Yes | Yes | Yes | Yes | Yes | Yes |
| [Flyweight](./structural/flyweight/) | Structural | Yes | Yes | Yes | Yes | Yes | Yes |
| [Proxy](./structural/proxy/) | Structural | Yes | Yes | Yes | Yes | Yes | Yes |
| [Chain of Responsibility](./behavioral/chain-of-responsibility/) | Behavioral | Yes | Yes | Yes | Yes | Yes | Yes |
| [Command](./behavioral/command/) | Behavioral | Yes | Yes | Yes | Yes | Yes | Yes |
| [Interpreter](./behavioral/interpreter/) | Behavioral | Yes | Yes | Yes | Yes | Yes | Yes |
| [Iterator](./behavioral/iterator/) | Behavioral | Yes | Yes | Yes | Yes | Yes | Yes |
| [Mediator](./behavioral/mediator/) | Behavioral | Yes | Yes | Yes | Yes | Yes | Yes |
| [Memento](./behavioral/memento/) | Behavioral | Yes | Yes | Yes | Yes | Yes | Yes |
| [Observer](./behavioral/observer/) | Behavioral | Yes | Yes | Yes | Yes | Yes | Yes |
| [State](./behavioral/state/) | Behavioral | Yes | Yes | Yes | Yes | Yes | Yes |
| [Strategy](./behavioral/strategy/) | Behavioral | Yes | Yes | Yes | Yes | Yes | Yes |
| [Template Method](./behavioral/template-method/) | Behavioral | Yes | Yes | Yes | Yes | Yes | Yes |
| [Visitor](./behavioral/visitor/) | Behavioral | Yes | Yes | Yes | Yes | Yes | Yes |

## Upgrade Path

Use this sequence when expanding pattern coverage:

1. Add missing tests to existing `v1-basic` examples before adding new versions.
2. Add a source-backed `v2-*` folder only when it teaches a distinct interview refinement, such as dependency injection, composition, or extensibility.
3. Add a source-backed `v3-*` folder only when it demonstrates production concerns such as concurrency, caching, observability, or failure handling.
4. Keep Java and Python parity for each new version unless the pattern README documents a deliberate language-specific exception.

Validation:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -B scripts/check_pattern_completion.py
```

Generate a plan or report showing actual behavior coverage evidence using opt-in modes:

```bash
python3 -B scripts/check_pattern_completion.py --evidence-plan
python3 -B scripts/check_pattern_completion.py --evidence-report
```
