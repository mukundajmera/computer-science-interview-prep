# Iterator Pattern - Theory & Interview Guide

## 📚 Core Concept

The Iterator pattern provides a way to access elements of a collection sequentially without exposing its underlying representation.

### Key Components

1. **Iterator (Interface)**: Declares traversal operations (next, hasNext)
2. **ConcreteIterator**: Implements traversal, tracks current position
3. **Aggregate (Interface)**: Declares method to create iterator
4. **ConcreteAggregate**: Collection that creates appropriate iterator

## 🎯 Problem It Solves

**Without Iterator:**
```java
// Client must know collection's internal structure
for (int i = 0; i < list.size(); i++) {
    Item item = list.get(i);  // Works for ArrayList
}

for (Node n = head; n != null; n = n.next) {
    Item item = n.value;  // Works for LinkedList
}
// Different code for each collection type!
```

**With Iterator:**
```java
Iterator<Item> iter = collection.iterator();
while (iter.hasNext()) {
    Item item = iter.next();  // Works for ANY collection!
}
```

## ✅ When to Use

1. **Hide collection structure** from clients
2. **Support multiple traversals** of same collection
3. **Provide uniform interface** for different collections
4. **Traverse without exposing** internal representation

## 🎤 Interview Q&A

### Q1: Internal vs External Iterator?

**A:**
| Internal Iterator | External Iterator |
|-------------------|-------------------|
| Collection controls iteration | Client controls iteration |
| Pass callback to collection | Client calls next() |
| `list.forEach(item -> ...)` | `while(iter.hasNext())` |
| Simpler for client | More flexible control |

### Q2: What's the Fail-Fast behavior in Java?

**A:** If collection is modified during iteration (except through iterator's remove()), `ConcurrentModificationException` is thrown. This prevents unpredictable behavior.

### Q3: Java Iterator vs Iterable?

**A:**
- `Iterable<T>`: Has `iterator()` method - enables for-each loop
- `Iterator<T>`: Has `hasNext()`, `next()`, `remove()` - performs traversal

```java
class MyCollection implements Iterable<Item> {
    public Iterator<Item> iterator() {
        return new MyIterator(this);
    }
}
```

### Q4: Python's iteration protocol?

**A:** Python uses:
- `__iter__()` - Returns iterator object (Iterable)
- `__next__()` - Returns next element (Iterator)
- Raises `StopIteration` when exhausted

## 💻 Code Patterns

### Java
```java
class MyIterator<T> implements Iterator<T> {
    private List<T> items;
    private int position = 0;
    
    public boolean hasNext() {
        return position < items.size();
    }
    
    public T next() {
        return items.get(position++);
    }
}
```

### Python
```python
class MyIterator:
    def __init__(self, data):
        self._data = data
        self._index = 0
    
    def __iter__(self):
        return self
    
    def __next__(self):
        if self._index >= len(self._data):
            raise StopIteration
        item = self._data[self._index]
        self._index += 1
        return item
```

### Python Generator (Preferred)
```python
def my_iterator(data):
    for item in data:
        yield item

# Or even simpler:
def filtered_items(data, predicate):
    for item in data:
        if predicate(item):
            yield item
```

## 🔗 Related Patterns

| Pattern | Relationship |
|---------|-------------|
| **Composite** | Often iterated using Iterator |
| **Factory Method** | Creates appropriate iterator |
| **Memento** | Iterator can be made resettable |
| **Visitor** | Alternative for complex operations |

---

[← Back to Iterator](./README.md)
