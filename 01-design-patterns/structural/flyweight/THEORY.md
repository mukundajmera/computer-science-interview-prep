# Flyweight Pattern - Theory

## 🎯 Problem

Your application creates millions of similar objects:
- Each has some shared properties (intrinsic)
- Each has unique properties (extrinsic)
- Memory consumption is too high

Example: Forest with 1 million trees
- Without Flyweight: 1M tree objects × 100 bytes = 100 MB
- With Flyweight: 10 tree types × 100 bytes + 1M positions × 12 bytes = 12 MB

---

## 💡 Solution

1. **Identify intrinsic state**: Shared, immutable (tree type, texture)
2. **Extract extrinsic state**: Per-instance (position, scale)
3. **Create factory**: Manages flyweight pool
4. **Pass extrinsic to operations**: Client provides context

```java
class TreeType {  // Flyweight (intrinsic)
    String name, texture, color;  // Shared
    void draw(int x, int y) { ... }  // x,y are extrinsic
}

class TreeFactory {
    static Map<String, TreeType> cache = new HashMap<>();
    
    static TreeType getTreeType(String name, String texture) {
        return cache.computeIfAbsent(
            name + texture, 
            k -> new TreeType(name, texture)
        );
    }
}
```

---

## 🎯 Interview Questions

### Q1: "How does String interning use Flyweight?"

```java
String s1 = "hello";
String s2 = "hello";
// s1 == s2 is true! Same object in string pool
```

"JVM maintains a pool of string literals. Same strings share memory."

### Q2: "Flyweight vs Object Pool?"

| Flyweight | Object Pool |
|-----------|-------------|
| Shares immutable objects | Manages reusable objects |
| Objects used simultaneously | Objects borrowed/returned |
| State separation | Same object reused |

---

## 🔗 Cross-References

- **LLD**: Game development, text editors
- **Related**: Factory, Singleton
