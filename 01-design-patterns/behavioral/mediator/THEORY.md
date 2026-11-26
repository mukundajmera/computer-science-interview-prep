# Mediator Pattern - Theory & Interview Guide

## 📚 Core Concept

The Mediator pattern defines an object that encapsulates how a set of objects interact. It promotes loose coupling by preventing objects from referring to each other directly.

### Key Components

1. **Mediator (Interface)**: Defines communication interface
2. **ConcreteMediator**: Implements coordination logic, knows all colleagues
3. **Colleague**: Objects that communicate via mediator

## 🎯 Problem It Solves

**Without Mediator:**
```java
// Every component knows about every other component
buttonA.onClick(() -> {
    textFieldB.validate();
    checkboxC.update();
    listD.refresh();
    buttonE.enable();
});
// N×(N-1) connections = massive coupling!
```

**With Mediator:**
```java
// Components only know the mediator
buttonA.onClick(() -> mediator.notify(this, "clicked"));
// Mediator coordinates all interactions
```

## 🏗️ Structure

```
         Without Mediator              With Mediator
         
    [A]──────[B]                  [A]     [B]
     │╲      ╱│                     ╲     ╱
     │ ╲    ╱ │                      ╲   ╱
     │  ╲  ╱  │          →        [Mediator]
     │   ╲╱   │                      ╱   ╲
     │   ╱╲   │                     ╱     ╲
    [C]──────[D]                  [C]     [D]
```

## ✅ When to Use

1. **Complex communication** between many objects
2. **Decoupling** objects that interact frequently
3. **Reusing components** that are tightly coupled
4. Examples: Chat rooms, air traffic control, UI dialogs

## 🎤 Interview Q&A

### Q1: Mediator vs Observer?

**A:**
| Mediator | Observer |
|----------|----------|
| Bi-directional communication | One-to-many notification |
| Colleagues know mediator | Observers don't know each other |
| Centralized control | Decentralized |
| Components can request actions | Components just react |

### Q2: Doesn't Mediator become a "God object"?

**A:** Risk exists! Mitigation strategies:
1. Split into multiple mediators by responsibility
2. Use Mediator only for coordination, not business logic
3. Keep mediator focused on routing, not processing

### Q3: Real-world examples?

**A:**
- **Air Traffic Control**: Planes communicate via ATC, not directly
- **Chat Server**: Users send messages through server
- **UI Dialogs**: Dialog box coordinates button/field interactions
- **Event Bus**: Components publish/subscribe via central bus

## 💻 Code Patterns

### Java
```java
interface Mediator {
    void notify(Component sender, String event);
}

class DialogMediator implements Mediator {
    private Button okButton;
    private TextField input;
    
    public void notify(Component sender, String event) {
        if (sender == input && event.equals("textChanged")) {
            okButton.setEnabled(!input.isEmpty());
        }
    }
}

class Button extends Component {
    public void click() {
        mediator.notify(this, "clicked");
    }
}
```

### Python
```python
class Mediator(ABC):
    @abstractmethod
    def notify(self, sender: object, event: str) -> None:
        pass

class ChatRoomMediator(Mediator):
    def __init__(self):
        self._users = []
    
    def notify(self, sender: 'User', event: str) -> None:
        if event == "message":
            for user in self._users:
                if user != sender:
                    user.receive(sender.last_message)
```

## 🔗 Related Patterns

| Pattern | Relationship |
|---------|-------------|
| **Facade** | Mediator's colleagues can call back; Facade is one-way |
| **Observer** | Mediator often uses Observer internally |
| **Command** | Commands can be passed through mediator |

---

[← Back to Mediator](./README.md)
