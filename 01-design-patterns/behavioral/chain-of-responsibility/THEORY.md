# Chain of Responsibility Pattern - Theory & Interview Guide

## 📚 Core Concept

The Chain of Responsibility pattern passes a request along a chain of handlers. Each handler decides to process the request or pass it to the next handler.

### Key Components

1. **Handler (Interface)**: Declares method for handling requests + link to successor
2. **ConcreteHandler**: Either handles request or passes to successor
3. **Client**: Initiates request to a handler in the chain

## 🎯 Problem It Solves

**Without Chain of Responsibility:**
```java
// Giant if-else or switch - hard to extend
if (requestType == AUTHENTICATION) {
    handleAuth(request);
} else if (requestType == AUTHORIZATION) {
    handleAuthz(request);
} else if (requestType == LOGGING) {
    handleLogging(request);
} else if (requestType == VALIDATION) {
    handleValidation(request);
}
// Adding new handler requires modifying this!
```

**With Chain:**
```java
Handler chain = new AuthHandler(
    new AuthzHandler(
        new LoggingHandler(null)
    )
);
chain.handle(request); // Each handler decides if it can handle
```

## 🏗️ Structure

```
┌────────────────────────────────────────────────────────────┐
│                                                            │
│  Request → [Handler1] → [Handler2] → [Handler3] → null    │
│               │             │             │                │
│            handle?       handle?       handle?             │
│               ▼             ▼             ▼                │
│            process       pass on       process             │
│                                                            │
└────────────────────────────────────────────────────────────┘
```

## ✅ When to Use

1. **Multiple handlers** can process a request
2. **Unknown handler** at compile time
3. **Decoupled sender and receivers**
4. **Chain can be configured dynamically**
5. Examples: Middleware, logging, event handling

## 🎤 Interview Q&A

### Q1: How is CoR used in real frameworks?

**A:**
- **Java Servlet Filters**: FilterChain
- **Spring Interceptors**: HandlerInterceptor chain
- **Express.js Middleware**: next() function
- **Logging Frameworks**: Log levels (DEBUG → INFO → WARN → ERROR)

### Q2: Can a handler both process AND pass on?

**A:** Yes! This is common in logging/middleware. A handler can pre-process, call next(), then post-process:
```java
void handle(Request r) {
    preProcess(r);      // Before
    next.handle(r);     // Pass on
    postProcess(r);     // After
}
```

### Q3: What happens if no handler processes the request?

**A:** Common strategies:
1. Do nothing (silent failure)
2. Default handler at end of chain
3. Throw exception
4. Return special "unhandled" response

### Q4: Decorator vs Chain of Responsibility?

**A:**
| Chain of Responsibility | Decorator |
|------------------------|-----------|
| Request can stop at any handler | All decorators run |
| One handler processes | Each decorator adds behavior |
| Unknown which will handle | All wrappers contribute |

## 💻 Code Patterns

### Java
```java
abstract class Handler {
    protected Handler next;
    
    public Handler setNext(Handler next) {
        this.next = next;
        return next; // Fluent chaining
    }
    
    public void handle(Request request) {
        if (canHandle(request)) {
            doHandle(request);
        } else if (next != null) {
            next.handle(request);
        }
    }
    
    protected abstract boolean canHandle(Request request);
    protected abstract void doHandle(Request request);
}
```

### Python
```python
class Handler(ABC):
    def __init__(self, next_handler=None):
        self._next = next_handler
    
    def handle(self, request):
        if self.can_handle(request):
            return self.do_handle(request)
        elif self._next:
            return self._next.handle(request)
        return None
    
    @abstractmethod
    def can_handle(self, request) -> bool:
        pass
    
    @abstractmethod
    def do_handle(self, request):
        pass
```

## 🔗 Related Patterns

| Pattern | Relationship |
|---------|-------------|
| **Composite** | CoR often uses composite structure |
| **Command** | Request can be Command object |
| **Decorator** | Similar structure, different intent |

---

[← Back to Chain of Responsibility](./README.md)
