# State Pattern - Theory & Interview Guide

## 📚 Core Concept

The State pattern allows an object to alter its behavior when its internal state changes. The object will appear to change its class.

### Key Components

1. **Context**: Maintains a reference to current state object
2. **State**: Interface defining state-specific behavior
3. **ConcreteState**: Implements behavior for a particular state

## 🎯 Problem It Solves

**Without State:**
```java
class Document {
    String state = "DRAFT";
    
    void publish() {
        if (state.equals("DRAFT")) {
            state = "REVIEW";
        } else if (state.equals("REVIEW")) {
            state = "PUBLISHED";
        }
        // More conditionals as states grow
    }
}
```

**With State:**
```java
interface State {
    void publish(Document doc);
}

class DraftState implements State {
    void publish(Document doc) {
        doc.setState(new ReviewState());
    }
}
```

## 🎤 Interview Q&A

### Q1: State vs Strategy - What's the difference?
**A:**
- **State**: States know about each other and trigger transitions
- **Strategy**: Strategies are independent, client chooses which to use
- **Intent**: State = behavior changes with internal state; Strategy = algorithm selection

### Q2: Who is responsible for state transitions?
**A:** Either:
1. **State objects** (more common): Each state knows what comes next
2. **Context**: Centralizes transition logic
3. **External**: Client triggers transitions

---

[← Back to State](./README.md)

---

## Interview Lens

- Use when behavior must change based on explicit state transitions.
- Keep transition rules local to states or a single coordinator, not both.
- Strong follow-up answer includes invalid-transition handling and observability.
