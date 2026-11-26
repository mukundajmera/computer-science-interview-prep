# Adapter Pattern - Theory

## 🎯 Problem

You have an existing class with useful functionality, but its interface doesn't match what your code expects. You cannot modify the existing class (it's a third-party library, legacy code, or widely used).

### Example Scenario

```
Your Application uses:          Third-Party Library provides:
┌─────────────────────┐         ┌─────────────────────┐
│ interface MediaPlayer│         │ class VLCPlayer     │
│   play(filename)    │         │   playVLC(file)     │
│   stop()            │         │   stopVLC()         │
└─────────────────────┘         └─────────────────────┘

Problem: VLCPlayer doesn't implement MediaPlayer interface!
```

---

## 💡 Solution

Create an Adapter class that:
1. Implements the expected interface (Target)
2. Holds a reference to the incompatible class (Adaptee)
3. Translates calls from Target interface to Adaptee methods

```java
class VLCAdapter implements MediaPlayer {
    private VLCPlayer vlc = new VLCPlayer();
    
    @Override
    public void play(String filename) {
        vlc.playVLC(filename);  // Translate call
    }
    
    @Override
    public void stop() {
        vlc.stopVLC();  // Translate call
    }
}
```

---

## 🎯 Interview Questions

### Q1: "What's the difference between Adapter and Facade?"

**Answer**:
| Adapter | Facade |
|---------|--------|
| Makes one interface compatible with another | Simplifies a complex subsystem |
| Works with single class usually | Works with multiple classes |
| Changes interface | Provides new, simpler interface |
| Client knows it's adapting | Client sees simpler view |

### Q2: "When would you use Class Adapter over Object Adapter?"

**Answer**:
"Class Adapter (inheritance) is rare because:
1. Requires multiple inheritance (not available in Java)
2. Tightly couples adapter to specific adaptee
3. Can't adapt subclasses

I'd use it only when:
- Language supports multiple inheritance (C++)
- Need to override adaptee behavior
- Performance critical (no delegation overhead)"

### Q3: "Can you have a Two-Way Adapter?"

**Answer**:
"Yes, a two-way adapter implements both interfaces, allowing objects on either side to communicate. Useful when:
- Two systems need to interoperate
- Legacy migration where both old and new code coexist

```java
class TwoWayAdapter implements NewInterface, LegacyInterface {
    // Can work as adapter in both directions
}
```"

### Q4: "How is Adapter different from Proxy?"

**Answer**:
| Adapter | Proxy |
|---------|-------|
| Different interface | Same interface |
| Structural compatibility | Access control or lazy loading |
| Wraps incompatible class | Wraps compatible class |

### Q5: "Give a real-world example of Adapter pattern"

**Answer**:
"**Power Adapter**: European devices (220V, round pins) with US outlets (110V, flat pins). The adapter:
- Has the interface the outlet expects (flat pins)
- Internally connects to the device (round pins)
- Translates voltage (220V ↔ 110V)

In code: JDBC drivers adapt vendor-specific database protocols to standard JDBC interface."

---

## ⚠️ Common Pitfalls

1. **Over-adapting**: Don't use adapter when you can modify the original class
2. **Too many adapters**: If you need many adapters, consider redesigning interfaces
3. **Hiding complexity**: Adapter should translate, not add complex logic
4. **Breaking Liskov**: Ensure adapted behavior truly matches expected interface

---

## 🔗 Cross-References

- **LLD Projects**: Payment gateways, third-party integrations
- **Related Patterns**: Bridge, Decorator, Proxy
- **Theory**: Open/Closed Principle (extend without modifying)
