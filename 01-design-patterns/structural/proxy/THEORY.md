# Proxy Pattern - Theory

## 🎯 Problem

You need to control access to an object:
- Expensive to create (lazy initialization)
- Remote location (network proxy)
- Access restrictions needed (protection proxy)
- Additional operations before/after (logging, caching)

---

## 💡 Solution

Create a proxy class that:
1. Implements the same interface as the real object
2. Contains a reference to the real object
3. Controls access and delegates when appropriate

```java
interface Image { void display(); }

class RealImage implements Image {
    RealImage(String file) { loadFromDisk(file); }  // Expensive!
}

class ProxyImage implements Image {
    private RealImage real;
    private String file;
    
    void display() {
        if (real == null) real = new RealImage(file);  // Lazy load
        real.display();
    }
}
```

---

## 🎯 Interview Questions

### Q1: "What are the different types of proxies?"

**Answer**:
1. **Virtual Proxy**: Lazy loading expensive objects
2. **Protection Proxy**: Access control based on permissions
3. **Remote Proxy**: Represent object in different address space
4. **Caching Proxy**: Cache expensive operation results
5. **Smart Reference**: Additional actions (reference counting, locking)

### Q2: "How is Proxy different from Adapter?"

| Proxy | Adapter |
|-------|---------|
| Same interface | Different interfaces |
| Controls access | Changes interface |
| Transparent to client | Enables incompatible objects |

### Q3: "When would you use a Proxy over a Decorator?"

"Proxy controls access; Decorator adds behavior. Use Proxy when:
- Lazy loading is needed
- Access control required
- Remote object representation
- You control lifecycle of real object"

---

## 🔗 Cross-References

- **LLD Projects**: File systems, database caching
- **Related**: Adapter, Decorator, Facade
