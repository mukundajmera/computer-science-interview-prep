# Observer Pattern - Theory & Interview Guide

## 📚 Core Concept

The Observer pattern defines a one-to-many dependency between objects so that when one object (the subject) changes state, all its dependents (observers) are notified and updated automatically.

### Key Components

1. **Subject (Observable)**: Maintains list of observers and notifies them of state changes
2. **Observer**: Interface defining update method called when subject changes
3. **ConcreteSubject**: Stores state of interest to observers
4. **ConcreteObserver**: Implements update to sync with subject's state

## 🎯 Problem It Solves

**Without Observer:**
```java
class StockData {
    void updatePrice(double price) {
        this.price = price;
        // Tight coupling to all displays
        phoneApp.update(price);
        webDisplay.update(price);
        emailAlert.check(price);
        // Must modify this class for each new display!
    }
}
```

**With Observer:**
```java
class StockData {
    private List<Observer> observers;
    
    void updatePrice(double price) {
        this.price = price;
        notifyObservers();  // All observers notified automatically
    }
}
```

## 🏗️ Push vs Pull Models

### Push Model
Subject sends detailed data with notification:
```java
observer.update(temperature, humidity, pressure);
```
- **Pros**: Observer has all needed data immediately
- **Cons**: May send data observer doesn't need

### Pull Model
Subject sends minimal notification, observer pulls data:
```java
observer.update();  // Observer calls subject.getTemperature()
```
- **Pros**: Observer gets only what it needs
- **Cons**: Observer needs subject reference, more method calls

## ✅ Benefits

1. **Loose Coupling**: Subject and observers only know interface
2. **Open/Closed**: Add observers without modifying subject
3. **Dynamic Relationships**: Add/remove observers at runtime
4. **Broadcast Communication**: One notification reaches many observers

## ❌ Drawbacks

1. **Unexpected Updates**: Cascading updates can be hard to trace
2. **Memory Leaks**: Forgotten observers remain attached
3. **Order Dependency**: Notification order may not be guaranteed
4. **Performance**: Many observers = many notifications

## 🎤 Interview Q&A

### Q1: Observer vs Pub/Sub - What's the difference?
**A:** 
- **Observer**: Subject directly notifies observers; tight coupling to interface
- **Pub/Sub**: Publishers and subscribers don't know each other; message broker mediates

### Q2: How do you prevent memory leaks in Observer?
**A:** 
- Use weak references for observer list
- Provide explicit `detach()` and call it when observer is destroyed
- In Java, use `WeakReference<Observer>` or frameworks that handle this

### Q3: How do you ensure thread safety in Observer?
**A:**
```java
// Option 1: Synchronized
private synchronized void notifyObservers() {
    for (Observer o : new ArrayList<>(observers)) {
        o.update();
    }
}

// Option 2: CopyOnWriteArrayList
private List<Observer> observers = new CopyOnWriteArrayList<>();
```

### Q4: When would Observer NOT be appropriate?
**A:**
- Need guaranteed delivery of notifications
- Order of notification matters
- Only one observer that never changes
- Performance-critical with many observers

### Q5: How does Observer relate to Reactive Programming?
**A:** Reactive programming is essentially Observer pattern at scale. RxJava's Observable/Observer, JavaScript's RxJS, and even Promises are built on observer concepts.

## 💻 Code Patterns

### Java - Classic
```java
interface Observer {
    void update(Object data);
}

class Subject {
    private List<Observer> observers = new ArrayList<>();
    
    public void attach(Observer o) { observers.add(o); }
    public void detach(Observer o) { observers.remove(o); }
    
    protected void notifyObservers(Object data) {
        for (Observer o : observers) o.update(data);
    }
}
```

### Python - Callable observers
```python
class Subject:
    def __init__(self):
        self._observers = []
    
    def attach(self, callback): 
        self._observers.append(callback)
    
    def notify(self, data):
        for callback in self._observers:
            callback(data)

# Usage
subject = Subject()
subject.attach(lambda x: print(f"Got: {x}"))
subject.notify("Hello")
```

### JavaScript - EventEmitter style
```javascript
class EventEmitter {
    constructor() { this.events = {}; }
    on(event, callback) {
        this.events[event] = this.events[event] || [];
        this.events[event].push(callback);
    }
    emit(event, data) {
        (this.events[event] || []).forEach(cb => cb(data));
    }
}
```

## 🔗 Related Patterns

| Pattern | Relationship |
|---------|-------------|
| **Mediator** | Centralizes observer logic; reduces direct observer references |
| **Singleton** | Subject is often a singleton |
| **MVC** | Model is subject; Views are observers |
| **Event Sourcing** | Built on observer concepts |

---

[← Back to Observer](./README.md)

---

## Interview Lens

- Use when one change source fan-outs to multiple dependent consumers.
- Clarify push vs pull update model and unsubscribe lifecycle handling.
- Mention delivery guarantees (best-effort vs durable) when discussing real systems.
