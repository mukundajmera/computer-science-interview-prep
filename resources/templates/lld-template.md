# 📝 LLD Practice Template

Use this template to practice Low-Level Design problems.

---

## Problem: [Problem Name]

**Date:** ___  
**Time spent:** ___

---

## 1. 📝 Requirements Clarification

### Functional Requirements
*What should the system do?*

- [ ] Requirement 1: ___
- [ ] Requirement 2: ___
- [ ] Requirement 3: ___
- [ ] Requirement 4: ___

### Non-Functional Requirements
*Constraints and quality attributes*

- Concurrency needed? ___
- Performance requirements? ___
- Extensibility requirements? ___

### Clarifying Questions Asked
1. Q: ___  A: ___
2. Q: ___  A: ___

---

## 2. 🎯 Core Entities

*Identify nouns from requirements*

| Entity | Attributes | Behaviors |
|--------|------------|-----------|
| ___ | ___ | ___ |
| ___ | ___ | ___ |
| ___ | ___ | ___ |

---

## 3. 🔗 Relationships

### Entity Relationships

```
Entity1 (1) ─────── (n) Entity2
        └── relationship type

Entity3 ───inherits─── Entity4
```

### Relationship Table

| Entity A | Relationship | Entity B | Type |
|----------|--------------|----------|------|
| ___ | has | ___ | Composition |
| ___ | uses | ___ | Aggregation |
| ___ | is-a | ___ | Inheritance |

---

## 4. 🎨 Design Patterns Used

| Pattern | Why Using It | Applied To |
|---------|--------------|------------|
| ___ | ___ | ___ |
| ___ | ___ | ___ |

---

## 5. 📐 Class Design

### Class 1: ___

```java
public class ClassName {
    // Attributes
    private Type attribute1;
    private Type attribute2;
    
    // Constructor
    public ClassName(params) {
        
    }
    
    // Methods
    public ReturnType methodName(params) {
        
    }
}
```

### Class 2: ___

```java
public class ClassName {
    // Attributes
    
    // Constructor
    
    // Methods
}
```

### Enums

```java
public enum EnumName {
    VALUE1,
    VALUE2,
    VALUE3
}
```

### Interfaces

```java
public interface InterfaceName {
    ReturnType methodName(params);
}
```

---

## 6. ⚠️ Edge Cases

| Edge Case | How Handled |
|-----------|-------------|
| Null input | ___ |
| Empty collection | ___ |
| Duplicate entries | ___ |
| Concurrent access | ___ |
| Invalid state | ___ |

---

## 7. ⚡ Optimizations

### Time Complexity

| Operation | Current | After Optimization |
|-----------|---------|-------------------|
| ___ | O(?) | O(?) |
| ___ | O(?) | O(?) |

### Space Complexity

| Component | Current | After Optimization |
|-----------|---------|-------------------|
| ___ | O(?) | O(?) |

### Data Structure Choices

| Used | For | Why |
|------|-----|-----|
| HashMap | ___ | O(1) lookups |
| ___ | ___ | ___ |

---

## 8. 📊 Class Diagram

*Draw or describe the class diagram*

```
┌─────────────────┐
│    ClassName    │
├─────────────────┤
│ - attribute1    │
│ - attribute2    │
├─────────────────┤
│ + method1()     │
│ + method2()     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  ChildClass     │
└─────────────────┘
```

---

## 9. ❓ Follow-up Questions

**Q1:** What if we need to add ___?
**A1:** ___

**Q2:** How would you handle ___?
**A2:** ___

---

## 10. 🔄 Self-Review

### What went well?
- 

### What could be improved?
- 

### Lessons learned?
- 

---

*Compare with solution and note differences!*
