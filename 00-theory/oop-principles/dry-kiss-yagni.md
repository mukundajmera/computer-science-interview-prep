# DRY, KISS, and YAGNI Principles

Three essential software engineering heuristics that balance the SOLID principles, guiding engineers toward pragmatic, maintainable, and cost-effective system designs.

---

## 🔁 DRY - Don't Repeat Yourself

> **Every piece of knowledge or business rule must have a single, unambiguous, authoritative representation within a system.**

### The Problem: Knowledge Duplication

#### Java
```java
// ❌ Code duplication - identical business rules duplicated across classes
class UserService {
    public void createUser(String email) {
        if (email == null || !email.contains("@") || email.length() < 5) {
            throw new IllegalArgumentException("Invalid email format");
        }
    }
}

class NewsletterService {
    public void subscribe(String email) {
        if (email == null || !email.contains("@") || email.length() < 5) {
            throw new IllegalArgumentException("Invalid email format");
        }
    }
}
```

#### Python
```python
# ❌ Code duplication - email validation duplicated
class UserService:
    def create_user(self, email: str) -> None:
        if not email or "@" not in email or len(email) < 5:
            raise ValueError("Invalid email format")


class NewsletterService:
    def subscribe(self, email: str) -> None:
        if not email or "@" not in email or len(email) < 5:
            raise ValueError("Invalid email format")
```

---

### The Solution: Authoritative Single Source of Truth

#### Java
```java
// ✅ Single authoritative validator
public final class EmailValidator {
    private EmailValidator() {}

    public static boolean isValid(String email) {
        return email != null && email.contains("@") && email.length() >= 5;
    }

    public static void validate(String email) {
        if (!isValid(email)) {
            throw new IllegalArgumentException("Invalid email: " + email);
        }
    }
}

class UserService {
    public void createUser(String email) {
        EmailValidator.validate(email);
    }
}

class NewsletterService {
    public void subscribe(String email) {
        EmailValidator.validate(email);
    }
}
```

#### Python
```python
# ✅ Single authoritative validator
class EmailValidator:
    @staticmethod
    def is_valid(email: str) -> bool:
        return bool(email and "@" in email and len(email) >= 5)

    @classmethod
    def validate(cls, email: str) -> None:
        if not cls.is_valid(email):
            raise ValueError(f"Invalid email: {email}")


class UserService:
    def create_user(self, email: str) -> None:
        EmailValidator.validate(email)


class NewsletterService:
    def subscribe(self, email: str) -> None:
        EmailValidator.validate(email)
```

---

### ⚠️ The Premature Abstraction Trap: Accidental Duplication

Not all similar code represents shared domain knowledge. Two functions that coincidentally look alike may evolve for completely different business reasons.

> *"Duplication is far cheaper than the wrong abstraction."* — **Sandi Metz**

```mermaid
flowchart TD
    Start{"Encountering duplicated or similar code"} --> Instances{"How many times has this logic been written?"}

    Instances -->|First Time (N = 1)| WriteOnce["Write it simply. No abstraction."]
    Instances -->|Second Time (N = 2)| Tolerate["Tolerate Duplication!\nSimilarities may be accidental.\nWait for requirements to stabilize."]
    Instances -->|Third Time (N = 3+)| CheckContext{"Do all 3 instances share the same fundamental reason to change?"}

    CheckContext -->|No: Different domain reasons| KeepSeparate["Keep separate! Avoid unifying unrelated domains under a leaky generic interface."]
    CheckContext -->|Yes: Shared authoritative concept| RefactorDRY["Refactor: Extract a single clean, well-tested abstraction or utility."]

    style WriteOnce fill:#e3f2fd,stroke:#1565c0
    style Tolerate fill:#fff3e0,stroke:#e65100
    style KeepSeparate fill:#ffebee,stroke:#c62828
    style RefactorDRY fill:#e8f5e9,stroke:#2e7d32
```

#### Java (Accidental Duplication vs True Duplication)
```java
// Coincidentally similar checks, but distinct domain responsibilities
class OrderValidator {
    void validate(Order order) {
        if (order.getAmount() <= 0) throw new IllegalArgumentException("Order cannot be free");
    }
}

class RefundValidator {
    void validate(Refund refund) {
        // Looks similar to OrderValidator, but evolves under accounting/compliance rules!
        if (refund.getAmount() <= 0) throw new IllegalArgumentException("Refund must be positive");
    }
}
```

#### Python (Accidental Duplication vs True Duplication)
```python
class OrderValidator:
    def validate(self, amount: float) -> None:
        if amount <= 0:
            raise ValueError("Order must be greater than zero")


class RefundValidator:
    # Separate domain entity: forcing inheritance or a shared base here is premature coupling
    def validate(self, amount: float) -> None:
        if amount <= 0:
            raise ValueError("Refund must be greater than zero")
```

---

## 💋 KISS - Keep It Simple, Stupid

> **Simplicity is a prerequisite for reliability. Favor obvious, readable code over speculative architectural complexity.**

### The Problem: Over-Engineered Enterprise Complexity

#### Java
```java
// ❌ 4 layers of design patterns for a string trim
class UserNameProcessor {
    private final NormalizerStrategyFactory factory;
    private final CacheManager cacheManager;

    public String processName(String name) {
        return cacheManager.getOrCompute(name, () -> factory.getStrategy().normalize(name));
    }
}
```

#### Python
```python
# ❌ Over-engineered factory and visitor for a basic string transformation
class NameTransformationVisitor:
    def visit(self, name_token: str) -> str:
        return name_token.strip().lower()


class ComplexUserNameProcessor:
    def __init__(self, visitor: NameTransformationVisitor) -> None:
        self._visitor = visitor

    def process(self, raw_name: str) -> str:
        return self._visitor.visit(raw_name)
```

---

### The Solution: Pragmatic Simplicity

#### Java
```java
// ✅ Clean, readable, zero indirection
public class UserNameProcessor {
    public static String processName(String name) {
        if (name == null) return "";
        return name.strip().toLowerCase();
    }
}
```

#### Python
```python
# ✅ Idiomatic, clear, instantly understandable
def process_user_name(name: str | None) -> str:
    return name.strip().lower() if name else ""
```

---

## 🚫 YAGNI - You Aren't Gonna Need It

> **Always implement things when you actually need them, never when you just foresee that you might need them.**

### The Problem: Speculative Generality

#### Java
```java
// ❌ Implementing hypothetical features that were never requested
class UserService {
    public void createUser(User u) { /* required */ }
    public User getUser(String id) { /* required */ }

    // Unrequested speculative features that accumulate technical debt and bugs:
    public void exportToCsv(String id) { throw new UnsupportedOperationException(); }
    public void convertToXml(User u) { throw new UnsupportedOperationException(); }
    public void backupToSecondaryCloud() { throw new UnsupportedOperationException(); }
}
```

#### Python
```python
# ❌ Speculative methods cluttering domain logic
class UserService:
    def create_user(self, user_id: str) -> None:
        pass

    def get_user(self, user_id: str) -> dict:
        return {}

    # Speculative additions nobody asked for:
    def export_to_parquet(self) -> bytes:
        raise NotImplementedError

    def stream_to_kafka_backup(self) -> None:
        raise NotImplementedError
```

---

### The Solution: Design for Extensibility, Implement for Reality

#### Java
```java
// ✅ Implement interface for extensibility; implement only active provider
interface PaymentGateway {
    boolean charge(double amount);
}

// Active production provider
class StripeGateway implements PaymentGateway {
    public boolean charge(double amount) { return true; }
}

// Do NOT implement PayPalGateway, CryptoGateway, or Alipay until business contracts are signed!
```

#### Python
```python
from abc import ABC, abstractmethod


# ✅ Clean interface leaves room for extension without implementing speculative code
class PaymentGateway(ABC):
    @abstractmethod
    def charge(self, amount: float) -> bool:
        pass


class StripeGateway(PaymentGateway):
    def charge(self, amount: float) -> bool:
        return True


# PayPalGateway, ApplePayGateway will be written ONLY when needed.
```

---

## ⚖️ Summary Comparison

| Principle | Core Question | Primary Target | Cardinal Rule |
|---|---|---|---|
| **DRY** | *"Is this business knowledge duplicated?"* | Maintainability & Consistency | Apply the Rule of Three; do not couple disparate domains. |
| **KISS** | *"Is this the simplest solution that works?"* | Readability & Cognitive Load | Eliminate unnecessary design patterns and layers. |
| **YAGNI** | *"Is this feature required today?"* | Scope & Engineering Velocity | Build for current requirements, not hypothetical futures. |

---

## Cross-References

- [SOLID Principles: SRP & Interface Segregation](./solid-principles.md)
- [Composition vs Inheritance](./composition-vs-inheritance.md)
- [Encapsulation & Abstraction](./encapsulation-abstraction.md)
