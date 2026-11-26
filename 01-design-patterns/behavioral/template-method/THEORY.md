# Template Method Pattern - Theory & Interview Guide

## 📚 Core Concept

The Template Method pattern defines the skeleton of an algorithm in a base class, letting subclasses override specific steps without changing the algorithm's structure.

### Key Components

1. **AbstractClass**: Defines template method and abstract/hook steps
2. **ConcreteClass**: Implements abstract steps, optionally overrides hooks
3. **Template Method**: Fixed algorithm calling abstract and hook methods

## 🎯 Problem It Solves

**Without Template Method:**
```java
// Duplicated algorithm structure across classes
class CSVExporter {
    void export() {
        validateData();      // Same
        openFile("csv");     // Different
        writeHeader();       // Same
        writeCSVRows();      // Different
        closeFile();         // Same
    }
}

class XMLExporter {
    void export() {
        validateData();      // Same (duplicated!)
        openFile("xml");     // Different
        writeHeader();       // Same (duplicated!)
        writeXMLNodes();     // Different
        closeFile();         // Same (duplicated!)
    }
}
```

**With Template Method:**
```java
abstract class DataExporter {
    // Template method - defines algorithm skeleton
    public final void export() {
        validateData();      // Common
        openFile();          // Abstract - subclass implements
        writeHeader();       // Common
        writeData();         // Abstract - subclass implements
        closeFile();         // Common
    }
}
```

## 🏗️ Structure

```
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│   ┌───────────────────────────────────┐                     │
│   │        AbstractClass              │                     │
│   ├───────────────────────────────────┤                     │
│   │ + templateMethod() {              │  ← final (don't     │
│   │     step1()                       │    override)        │
│   │     step2()  // abstract          │                     │
│   │     step3()  // hook              │                     │
│   │   }                               │                     │
│   │ + step1() { ... }                 │  ← concrete         │
│   │ + step2()          // abstract    │  ← must override    │
│   │ + step3() { }      // hook        │  ← may override     │
│   └─────────────┬─────────────────────┘                     │
│                 │                                           │
│        ┌────────┴────────┐                                  │
│        │                 │                                  │
│   ┌────┴─────┐      ┌────┴─────┐                            │
│   │ConcreteA │      │ConcreteB │                            │
│   ├──────────┤      ├──────────┤                            │
│   │+ step2() │      │+ step2() │  ← different impl          │
│   │+ step3() │      └──────────┘  ← uses default hook       │
│   └──────────┘                                              │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## ✅ When to Use

1. **Common algorithm, varying steps**
2. **Code reuse** with controlled variation
3. **Enforcing algorithm structure**
4. Examples: Frameworks, data parsers, test fixtures

## 🎤 Interview Q&A

### Q1: Abstract steps vs Hook methods?

**A:**
| Abstract Step | Hook |
|---------------|------|
| Must be overridden | Optional override |
| `abstract void step()` | `void hook() { }` |
| Subclass provides impl | Default empty/basic impl |
| Forces variation | Allows variation |

### Q2: Template Method vs Strategy?

**A:**
| Template Method | Strategy |
|-----------------|----------|
| Uses inheritance | Uses composition |
| Subclass overrides | Algorithm object swapped |
| Compile-time binding | Runtime binding |
| White-box reuse | Black-box reuse |

### Q3: How do you prevent template method from being overridden?

**A:** Make it `final` in Java or non-overridable:
```java
public final void templateMethod() { ... }
```

### Q4: Real-world examples?

**A:**
- **JUnit**: `setUp()`, `tearDown()` are hooks
- **Servlet**: `doGet()`, `doPost()` in HttpServlet
- **React**: lifecycle methods (componentDidMount)
- **Spring**: `AbstractController` with handleRequest template

## 💻 Code Patterns

### Java
```java
abstract class DataMiner {
    // Template method - final to prevent override
    public final void mine() {
        openFile();
        extractData();
        parseData();
        analyzeData();
        sendReport();
        closeFile();
    }
    
    abstract void openFile();      // Must implement
    abstract void extractData();   // Must implement
    abstract void closeFile();     // Must implement
    
    // Hook - optional override
    void parseData() { }
    
    // Common implementation
    void analyzeData() {
        System.out.println("Analyzing data...");
    }
    
    void sendReport() {
        System.out.println("Sending report...");
    }
}

class PDFMiner extends DataMiner {
    void openFile() { System.out.println("Opening PDF..."); }
    void extractData() { System.out.println("Extracting PDF text..."); }
    void closeFile() { System.out.println("Closing PDF..."); }
}
```

### Python
```python
from abc import ABC, abstractmethod

class DataMiner(ABC):
    def mine(self):
        """Template method - defines algorithm skeleton."""
        self.open_file()
        self.extract_data()
        self.parse_data()
        self.analyze_data()
        self.send_report()
        self.close_file()
    
    @abstractmethod
    def open_file(self): pass
    
    @abstractmethod
    def extract_data(self): pass
    
    @abstractmethod
    def close_file(self): pass
    
    # Hook - optional override
    def parse_data(self):
        pass
    
    # Common implementations
    def analyze_data(self):
        print("Analyzing data...")
    
    def send_report(self):
        print("Sending report...")
```

## 🔗 Related Patterns

| Pattern | Relationship |
|---------|-------------|
| **Strategy** | Alternative using composition |
| **Factory Method** | Specialized template method |
| **Hook** | Template method uses hooks |

---

[← Back to Template Method](./README.md)
