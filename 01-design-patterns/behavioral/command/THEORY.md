# Command Pattern - Theory & Interview Guide

## 📚 Core Concept

The Command pattern encapsulates a request as an object, thereby letting you parameterize clients with different requests, queue or log requests, and support undoable operations.

### Key Components

1. **Command**: Interface declaring execution method
2. **ConcreteCommand**: Implements execution by invoking receiver methods
3. **Receiver**: Knows how to perform the actual work
4. **Invoker**: Asks command to carry out the request
5. **Client**: Creates command and sets its receiver

## 🎯 Problem It Solves

**Without Command:**
```java
class Button {
    void onClick() {
        // Direct call - hard to change, can't undo
        light.turnOn();
    }
}
```

**With Command:**
```java
class Button {
    private Command command;
    
    void onClick() {
        command.execute();  // Flexible, undoable
    }
}
```

## ✅ Benefits

1. **Decoupling**: Invoker doesn't need to know receiver details
2. **Undo/Redo**: Store state and reverse operations
3. **Composition**: Combine commands into macros
4. **Queueing**: Execute commands later or in sequence
5. **Logging**: Record commands for audit or replay

## 🎤 Interview Q&A

### Q1: How do you implement undo in Command pattern?
**A:**
```java
interface Command {
    void execute();
    void undo();
}

class Invoker {
    private Stack<Command> history = new Stack<>();
    
    void execute(Command cmd) {
        cmd.execute();
        history.push(cmd);
    }
    
    void undo() {
        if (!history.isEmpty()) {
            history.pop().undo();
        }
    }
}
```

### Q2: When would you NOT use Command?
**A:**
- Simple operations that don't need undo/queue
- Direct method calls are sufficient
- No need for operation history

### Q3: How does Command relate to Strategy?
**A:**
- **Strategy**: Defines HOW to do something (algorithms)
- **Command**: Defines WHAT to do (encapsulates action + receiver)

---

[← Back to Command](./README.md)
