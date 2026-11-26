# Singleton Pattern - Theory & Interview Guide

## 📚 Core Concept

The Singleton pattern ensures a class has only one instance and provides a global point of access to that instance.

### Key Components

1. **Private Constructor**: Prevents external instantiation
2. **Static Instance**: Holds the single object
3. **Static Access Method**: Returns the instance (creates it if needed)

## 🎯 Problem It Solves

**Without Singleton:**
```java
// Multiple instances created - inconsistent state
DatabaseConnection conn1 = new DatabaseConnection(); // Instance 1
DatabaseConnection conn2 = new DatabaseConnection(); // Instance 2
// conn1 and conn2 have different connection pools!
```

**Problems:**
- Multiple objects consuming resources
- Inconsistent state across the application
- Race conditions when accessing shared resources
- Difficulty coordinating shared state

**With Singleton:**
```java
DatabaseConnection conn1 = DatabaseConnection.getInstance();
DatabaseConnection conn2 = DatabaseConnection.getInstance();
// conn1 == conn2 - Same instance, consistent state!
```

## 🏗️ Implementation Variants

### 1. Eager Initialization
```
┌────────────────────────────────────────┐
│  Instance created at class loading     │
│  + Simple, thread-safe                 │
│  - Resources used even if not needed   │
└────────────────────────────────────────┘
```

### 2. Lazy Initialization (Thread-Unsafe)
```
┌────────────────────────────────────────┐
│  Instance created on first access      │
│  + No wasted resources                 │
│  - NOT thread-safe!                    │
└────────────────────────────────────────┘
```

### 3. Double-Checked Locking
```
┌────────────────────────────────────────┐
│  Lazy + synchronized with volatile     │
│  + Thread-safe                         │
│  + Efficient (locks only once)         │
│  - Complex, easy to get wrong          │
└────────────────────────────────────────┘
```

### 4. Bill Pugh / Holder Pattern (Recommended for Java)
```
┌────────────────────────────────────────┐
│  Uses static inner class               │
│  + Thread-safe via class loading       │
│  + Lazy initialization                 │
│  + No synchronization overhead         │
└────────────────────────────────────────┘
```

### 5. Enum Singleton (Best for Java)
```
┌────────────────────────────────────────┐
│  Uses Java enum                        │
│  + Thread-safe by JVM                  │
│  + Serialization-safe                  │
│  + Reflection-safe                     │
│  - Cannot extend classes               │
└────────────────────────────────────────┘
```

## ✅ Benefits

1. **Guaranteed Single Instance**: Only one object exists
2. **Global Access Point**: Easy to access from anywhere
3. **Lazy Initialization**: Create only when needed
4. **State Consistency**: Single source of truth

## ❌ Drawbacks

1. **Global State**: Can hide dependencies (anti-pattern)
2. **Testing Difficulties**: Hard to mock and isolate
3. **Concurrency Issues**: Complex thread-safety requirements
4. **Violates SRP**: Class manages both logic AND lifecycle

## 🎤 Interview Q&A

### Q1: How do you make Singleton thread-safe?

**A:** Multiple approaches:
1. **Eager initialization** - Thread-safe, but not lazy
2. **Synchronized method** - Thread-safe, but slow
3. **Double-checked locking with volatile** - Thread-safe and efficient
4. **Bill Pugh (static inner class)** - Thread-safe via class loader
5. **Enum** - Thread-safe by JVM guarantees

### Q2: How do you prevent Singleton from being broken by reflection?

**A:** 
```java
// In constructor:
private Singleton() {
    if (instance != null) {
        throw new RuntimeException("Use getInstance() method");
    }
}
```
Or use Enum singleton - reflection cannot instantiate enums.

### Q3: How do you make Singleton serialization-safe?

**A:** Implement `readResolve()` method:
```java
protected Object readResolve() {
    return getInstance();
}
```
Or use Enum singleton - serialization is handled automatically.

### Q4: When would you NOT use Singleton?

**A:**
- When you need multiple instances in the future
- When the class has mutable state that varies per context
- When testability is crucial (dependency injection is better)
- In multi-classloader environments (creates multiple instances)

### Q5: Singleton vs Static Class - when to use which?

**A:**
| Singleton | Static Class |
|-----------|--------------|
| Can implement interfaces | Cannot |
| Can be lazy-loaded | Always loaded |
| Can be passed as parameter | Cannot |
| Can have state | Usually stateless |
| Polymorphism possible | Not possible |

Use Singleton when you need interface implementation, lazy loading, or polymorphism.

## 🔍 Common Mistakes

1. **Forgetting volatile** in double-checked locking
2. **Not handling serialization** - creates new instance on deserialize
3. **Not handling reflection** - can create second instance
4. **Forgetting clone protection** - implement clone() to throw exception
5. **Using in multi-classloader** environment without awareness

## 💻 Code Patterns

### Java - Bill Pugh (Recommended)
```java
public class Singleton {
    private Singleton() {}
    
    private static class Holder {
        private static final Singleton INSTANCE = new Singleton();
    }
    
    public static Singleton getInstance() {
        return Holder.INSTANCE;
    }
}
```

### Java - Enum (Best)
```java
public enum Singleton {
    INSTANCE;
    
    public void doSomething() {
        // business logic
    }
}
```

### Python - Module Level (Pythonic)
```python
# singleton_module.py
class _Singleton:
    def __init__(self):
        self.value = None

# Module-level instance
singleton = _Singleton()

# Usage: from singleton_module import singleton
```

### Python - Metaclass
```python
class SingletonMeta(type):
    _instances = {}
    
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]

class Singleton(metaclass=SingletonMeta):
    pass
```

## 🔗 Related Patterns

| Pattern | Relationship |
|---------|-------------|
| **Factory** | Often implemented as Singleton |
| **Abstract Factory** | Usually a Singleton |
| **Builder** | Director can be Singleton |
| **Facade** | Often implemented as Singleton |
| **State** | State objects often Singletons |

## 📁 Implementations

| Version | Description | Location |
|---------|-------------|----------|
| v1-basic | Eager initialization | [Java](./java/v1-basic/) / [Python](./python/v1-basic/) |
| v2-variant | Double-checked locking (Java) / __new__ (Python) | [Java](./java/v2-variant/) / [Python](./python/v2-variant/) |
| v3-advanced | Enum (Java) / Metaclass (Python) | [Java](./java/v3-advanced/) / [Python](./python/v3-advanced/) |

---

[← Back to Singleton](./README.md)

---

## Interview Lens

- Use only for truly shared system-wide state/control points.
- Mention testability and hidden dependency risks explicitly.
- Strong answer includes a non-Singleton alternative when feasible.
