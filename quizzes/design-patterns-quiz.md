# 🎨 Design Patterns Quiz

> **50 questions to test your design pattern knowledge**
> 
> ⏱️ Time: 60 minutes | ⭐⭐⭐ Difficulty

---

## Section 1: Pattern Identification (15 questions)

*Choose the pattern that best solves the given problem.*

---

### Question 1 ⭐
You need to ensure only one database connection exists throughout your application.

**A)** Factory Method
**B)** Singleton
**C)** Prototype
**D)** Builder

---

### Question 2 ⭐
You want to add new functionality to an object without modifying its class.

**A)** Adapter
**B)** Proxy
**C)** Decorator
**D)** Facade

---

### Question 3 ⭐
You need to create families of related objects (buttons, checkboxes, menus) for different operating systems (Windows, Mac, Linux).

**A)** Factory Method
**B)** Abstract Factory
**C)** Builder
**D)** Prototype

---

### Question 4 ⭐⭐
You have a legacy XML-based API but need to integrate with a modern JSON-based system.

**A)** Bridge
**B)** Adapter
**C)** Facade
**D)** Proxy

---

### Question 5 ⭐⭐
You want to notify multiple objects when a stock price changes.

**A)** Mediator
**B)** Chain of Responsibility
**C)** Observer
**D)** Command

---

### Question 6 ⭐⭐
You need to support undo/redo operations in a text editor.

**A)** Memento
**B)** Command
**C)** State
**D)** Both A and B

---

### Question 7 ⭐⭐
A vending machine behaves differently based on whether it has items, is waiting for payment, or is dispensing.

**A)** Strategy
**B)** State
**C)** Command
**D)** Template Method

---

### Question 8 ⭐⭐
You want to construct a complex SQL query with optional WHERE, ORDER BY, and LIMIT clauses.

**A)** Factory Method
**B)** Abstract Factory
**C)** Builder
**D)** Prototype

---

### Question 9 ⭐⭐
You need to provide a simplified interface to a complex subsystem of classes (database, cache, logging).

**A)** Adapter
**B)** Bridge
**C)** Facade
**D)** Composite

---

### Question 10 ⭐⭐
You want to represent a file system with files and folders, where folders can contain files or other folders.

**A)** Decorator
**B)** Composite
**C)** Flyweight
**D)** Bridge

---

### Question 11 ⭐⭐⭐
You need to defer object creation or control access to a resource-intensive object.

**A)** Decorator
**B)** Adapter
**C)** Proxy
**D)** Facade

---

### Question 12 ⭐⭐⭐
You want to swap sorting algorithms (quick sort, merge sort, bubble sort) at runtime.

**A)** State
**B)** Strategy
**C)** Template Method
**D)** Command

---

### Question 13 ⭐⭐⭐
You need to iterate through a collection without exposing its underlying structure.

**A)** Visitor
**B)** Iterator
**C)** Composite
**D)** Mediator

---

### Question 14 ⭐⭐⭐
You have many similar objects that consume too much memory (characters in a text editor).

**A)** Prototype
**B)** Flyweight
**C)** Singleton
**D)** Object Pool

---

### Question 15 ⭐⭐⭐
You need multiple handlers to process a request, and each handler decides whether to process or pass to the next.

**A)** Command
**B)** Mediator
**C)** Chain of Responsibility
**D)** Observer

---

## Section 2: Code Recognition (15 questions)

*Identify the design pattern implemented in each code snippet.*

---

### Question 16 ⭐
```java
public class DatabaseConnection {
    private static DatabaseConnection instance;
    private DatabaseConnection() {}
    public static synchronized DatabaseConnection getInstance() {
        if (instance == null) {
            instance = new DatabaseConnection();
        }
        return instance;
    }
}
```

**A)** Factory Method
**B)** Singleton
**C)** Prototype
**D)** Builder

---

### Question 17 ⭐⭐
```java
public interface PaymentStrategy {
    void pay(int amount);
}
public class CreditCardPayment implements PaymentStrategy {
    public void pay(int amount) { /* credit card logic */ }
}
public class PayPalPayment implements PaymentStrategy {
    public void pay(int amount) { /* PayPal logic */ }
}
public class ShoppingCart {
    private PaymentStrategy paymentStrategy;
    public void setPaymentStrategy(PaymentStrategy strategy) {
        this.paymentStrategy = strategy;
    }
    public void checkout(int amount) {
        paymentStrategy.pay(amount);
    }
}
```

**A)** State
**B)** Strategy
**C)** Command
**D)** Template Method

---

### Question 18 ⭐⭐
```java
public interface Coffee {
    double getCost();
    String getDescription();
}
public class SimpleCoffee implements Coffee {
    public double getCost() { return 2.0; }
    public String getDescription() { return "Simple Coffee"; }
}
public class MilkDecorator implements Coffee {
    private Coffee coffee;
    public MilkDecorator(Coffee coffee) { this.coffee = coffee; }
    public double getCost() { return coffee.getCost() + 0.5; }
    public String getDescription() { return coffee.getDescription() + ", Milk"; }
}
```

**A)** Adapter
**B)** Proxy
**C)** Decorator
**D)** Composite

---

### Question 19 ⭐⭐
```java
public interface Subject {
    void attach(Observer o);
    void detach(Observer o);
    void notifyObservers();
}
public class StockMarket implements Subject {
    private List<Observer> observers = new ArrayList<>();
    private double stockPrice;
    public void setStockPrice(double price) {
        this.stockPrice = price;
        notifyObservers();
    }
    public void notifyObservers() {
        for (Observer o : observers) o.update(stockPrice);
    }
}
```

**A)** Mediator
**B)** Observer
**C)** Pub-Sub
**D)** Command

---

### Question 20 ⭐⭐
```java
public abstract class DocumentFactory {
    public abstract Document createDocument();
}
public class PdfFactory extends DocumentFactory {
    public Document createDocument() { return new PdfDocument(); }
}
public class WordFactory extends DocumentFactory {
    public Document createDocument() { return new WordDocument(); }
}
```

**A)** Abstract Factory
**B)** Factory Method
**C)** Builder
**D)** Prototype

---

### Question 21 ⭐⭐
```java
public class Computer {
    private String cpu;
    private String ram;
    private String storage;
    
    private Computer(Builder builder) {
        this.cpu = builder.cpu;
        this.ram = builder.ram;
        this.storage = builder.storage;
    }
    
    public static class Builder {
        private String cpu;
        private String ram;
        private String storage;
        
        public Builder setCpu(String cpu) { this.cpu = cpu; return this; }
        public Builder setRam(String ram) { this.ram = ram; return this; }
        public Builder setStorage(String storage) { this.storage = storage; return this; }
        public Computer build() { return new Computer(this); }
    }
}
```

**A)** Factory Method
**B)** Abstract Factory
**C)** Builder
**D)** Prototype

---

### Question 22 ⭐⭐⭐
```java
public interface Command {
    void execute();
    void undo();
}
public class LightOnCommand implements Command {
    private Light light;
    public LightOnCommand(Light light) { this.light = light; }
    public void execute() { light.on(); }
    public void undo() { light.off(); }
}
public class RemoteControl {
    private Command command;
    public void setCommand(Command cmd) { this.command = cmd; }
    public void pressButton() { command.execute(); }
    public void pressUndo() { command.undo(); }
}
```

**A)** Strategy
**B)** Command
**C)** State
**D)** Memento

---

### Question 23 ⭐⭐⭐
```java
public interface Handler {
    void setNext(Handler handler);
    void handle(Request request);
}
public class AuthenticationHandler implements Handler {
    private Handler next;
    public void setNext(Handler handler) { this.next = handler; }
    public void handle(Request request) {
        if (canHandle(request)) { /* process */ }
        else if (next != null) { next.handle(request); }
    }
}
```

**A)** Decorator
**B)** Chain of Responsibility
**C)** Command
**D)** Mediator

---

### Question 24 ⭐⭐⭐
```java
public interface State {
    void insertCoin(VendingMachine context);
    void selectItem(VendingMachine context);
    void dispense(VendingMachine context);
}
public class NoCoinState implements State {
    public void insertCoin(VendingMachine context) {
        context.setState(new HasCoinState());
    }
    public void selectItem(VendingMachine context) {
        System.out.println("Insert coin first");
    }
}
```

**A)** Strategy
**B)** State
**C)** Command
**D)** Template Method

---

### Question 25 ⭐⭐⭐
```java
public class LegacyRectangle {
    public void draw(int x1, int y1, int x2, int y2) { /* legacy drawing */ }
}
public class RectangleAdapter implements Shape {
    private LegacyRectangle legacyRectangle;
    public RectangleAdapter(LegacyRectangle lr) { this.legacyRectangle = lr; }
    public void draw(int x, int y, int width, int height) {
        legacyRectangle.draw(x, y, x + width, y + height);
    }
}
```

**A)** Bridge
**B)** Adapter
**C)** Decorator
**D)** Proxy

---

### Question 26 ⭐⭐⭐
```java
public abstract class DataProcessor {
    public final void process() {
        readData();
        processData();
        writeData();
    }
    protected abstract void readData();
    protected abstract void processData();
    protected void writeData() { /* default implementation */ }
}
```

**A)** Strategy
**B)** State
**C)** Template Method
**D)** Factory Method

---

### Question 27 ⭐⭐⭐
```java
public class ImageProxy implements Image {
    private RealImage realImage;
    private String filename;
    public ImageProxy(String filename) { this.filename = filename; }
    public void display() {
        if (realImage == null) {
            realImage = new RealImage(filename); // lazy loading
        }
        realImage.display();
    }
}
```

**A)** Decorator
**B)** Adapter
**C)** Proxy
**D)** Facade

---

### Question 28 ⭐⭐⭐
```java
public interface GUIFactory {
    Button createButton();
    Checkbox createCheckbox();
    Menu createMenu();
}
public class WindowsFactory implements GUIFactory {
    public Button createButton() { return new WindowsButton(); }
    public Checkbox createCheckbox() { return new WindowsCheckbox(); }
    public Menu createMenu() { return new WindowsMenu(); }
}
```

**A)** Factory Method
**B)** Abstract Factory
**C)** Builder
**D)** Prototype

---

### Question 29 ⭐⭐⭐⭐
```java
public class CharacterFlyweight {
    private char symbol; // intrinsic state
    public CharacterFlyweight(char symbol) { this.symbol = symbol; }
    public void display(int fontSize, String color) { // extrinsic state
        System.out.println(symbol + " at size " + fontSize + " in " + color);
    }
}
public class CharacterFactory {
    private Map<java.lang.Character, CharacterFlyweight> pool = new HashMap<>();
    public CharacterFlyweight getCharacter(char c) {
        if (!pool.containsKey(c)) {
            pool.put(c, new CharacterFlyweight(c));
        }
        return pool.get(c);
    }
}
```

**A)** Prototype
**B)** Flyweight
**C)** Object Pool
**D)** Singleton

---

### Question 30 ⭐⭐⭐⭐
```java
public class TextEditor {
    private StringBuilder content;
    public Memento save() {
        return new Memento(content.toString());
    }
    public void restore(Memento memento) {
        this.content = new StringBuilder(memento.getState());
    }
}
public class Memento {
    private final String state;
    public Memento(String state) { this.state = state; }
    public String getState() { return state; }
}
```

**A)** Command
**B)** Memento
**C)** State
**D)** Prototype

---

## Section 3: Scenario Application (20 questions)

*Select the best pattern and explain your reasoning.*

---

### Question 31 ⭐⭐
**Scenario:** You're building a notification system that can send messages via Email, SMS, Push notifications, and Slack. Users should be able to switch notification methods at runtime.

Which pattern would you use?

**A)** Factory Method
**B)** Strategy
**C)** Observer
**D)** Command

**Explain your reasoning:** _______________________________________________

---

### Question 32 ⭐⭐
**Scenario:** A coffee shop allows customers to add various toppings (milk, sugar, whipped cream, chocolate) to a base coffee. Each topping has its own price.

Which pattern would you use?

**A)** Composite
**B)** Decorator
**C)** Builder
**D)** Factory Method

**Explain your reasoning:** _______________________________________________

---

### Question 33 ⭐⭐
**Scenario:** You're designing a document editor that supports multiple document types (PDF, Word, Excel). Each type has its own rendering and save logic.

Which pattern would you use?

**A)** Strategy
**B)** Abstract Factory
**C)** Factory Method
**D)** Template Method

**Explain your reasoning:** _______________________________________________

---

### Question 34 ⭐⭐
**Scenario:** An e-commerce platform processes orders through multiple stages: validation, payment, inventory check, and shipping. Each stage can approve or reject the order.

Which pattern would you use?

**A)** State
**B)** Command
**C)** Chain of Responsibility
**D)** Observer

**Explain your reasoning:** _______________________________________________

---

### Question 35 ⭐⭐⭐
**Scenario:** A trading platform needs to notify multiple dashboards, alerts, and analytics systems when a stock price changes.

Which pattern would you use?

**A)** Mediator
**B)** Observer
**C)** Command
**D)** Strategy

**Explain your reasoning:** _______________________________________________

---

### Question 36 ⭐⭐⭐
**Scenario:** You need to integrate with three different payment gateways (Stripe, PayPal, Square), each with different APIs.

Which pattern would you use?

**A)** Facade
**B)** Adapter
**C)** Bridge
**D)** Strategy

**Explain your reasoning:** _______________________________________________

---

### Question 37 ⭐⭐⭐
**Scenario:** A game has entities like Player, Enemy, NPC. You want to add new operations (save, render, AI behavior) without modifying these classes.

Which pattern would you use?

**A)** Decorator
**B)** Strategy
**C)** Visitor
**D)** Command

**Explain your reasoning:** _______________________________________________

---

### Question 38 ⭐⭐⭐
**Scenario:** A smart home system has devices (lights, thermostat, security) controlled via a universal remote. You want to support undo for all commands.

Which pattern would you use?

**A)** Strategy
**B)** Command
**C)** State
**D)** Memento

**Explain your reasoning:** _______________________________________________

---

### Question 39 ⭐⭐⭐
**Scenario:** An ATM machine behaves differently based on whether the user has inserted a card, entered PIN, or is withdrawing cash.

Which pattern would you use?

**A)** Strategy
**B)** State
**C)** Chain of Responsibility
**D)** Command

**Explain your reasoning:** _______________________________________________

---

### Question 40 ⭐⭐⭐
**Scenario:** You're building a report generator that creates reports in PDF, Excel, and HTML formats. The generation process involves: gathering data, formatting, and exporting.

Which pattern would you use?

**A)** Factory Method
**B)** Strategy
**C)** Template Method
**D)** Builder

**Explain your reasoning:** _______________________________________________

---

### Question 41 ⭐⭐⭐
**Scenario:** A logging framework needs to write logs to console, file, and remote server. You want to easily add new logging destinations.

Which pattern would you use?

**A)** Observer
**B)** Strategy
**C)** Chain of Responsibility
**D)** Decorator

**Explain your reasoning:** _______________________________________________

---

### Question 42 ⭐⭐⭐
**Scenario:** A drawing application has shapes (Circle, Rectangle, Triangle). Users can group shapes together and treat groups as single shapes.

Which pattern would you use?

**A)** Decorator
**B)** Composite
**C)** Flyweight
**D)** Bridge

**Explain your reasoning:** _______________________________________________

---

### Question 43 ⭐⭐⭐⭐
**Scenario:** A caching proxy that intercepts database calls, checks cache first, and only queries the database on cache miss.

Which pattern would you use?

**A)** Decorator
**B)** Adapter
**C)** Proxy
**D)** Facade

**Explain your reasoning:** _______________________________________________

---

### Question 44 ⭐⭐⭐⭐
**Scenario:** Creating game characters with various combinations of race, class, weapon, and armor. Some combinations are valid, others aren't.

Which pattern would you use?

**A)** Abstract Factory
**B)** Builder
**C)** Prototype
**D)** Factory Method

**Explain your reasoning:** _______________________________________________

---

### Question 45 ⭐⭐⭐⭐
**Scenario:** A music player supports different audio formats (MP3, WAV, FLAC). Each format has different decoding logic, but the playback interface remains the same.

Which pattern would you use?

**A)** Adapter
**B)** Strategy
**C)** Bridge
**D)** Template Method

**Explain your reasoning:** _______________________________________________

---

### Question 46 ⭐⭐⭐⭐
**Scenario:** A text editor needs snapshot functionality to save and restore document state at any point.

Which pattern(s) would you use?

**A)** Command only
**B)** Memento only
**C)** Command + Memento
**D)** State + Observer

**Explain your reasoning:** _______________________________________________

---

### Question 47 ⭐⭐⭐⭐
**Scenario:** A chat application where users can communicate only through a central server, not directly with each other.

Which pattern would you use?

**A)** Observer
**B)** Mediator
**C)** Chain of Responsibility
**D)** Command

**Explain your reasoning:** _______________________________________________

---

### Question 48 ⭐⭐⭐⭐
**Scenario:** An expense approval system where requests under $100 are auto-approved, $100-$1000 need manager approval, and >$1000 need director approval.

Which pattern would you use?

**A)** State
**B)** Strategy
**C)** Chain of Responsibility
**D)** Command

**Explain your reasoning:** _______________________________________________

---

### Question 49 ⭐⭐⭐⭐
**Scenario:** A graphics engine supports rendering on multiple platforms (OpenGL, DirectX, Vulkan) with different shape types (2D, 3D).

Which pattern would you use?

**A)** Abstract Factory
**B)** Bridge
**C)** Adapter
**D)** Strategy

**Explain your reasoning:** _______________________________________________

---

### Question 50 ⭐⭐⭐⭐
**Scenario:** A word processor where font objects are shared across the document to save memory, but each character can have different size and color.

Which pattern would you use?

**A)** Prototype
**B)** Flyweight
**C)** Singleton
**D)** Object Pool

**Explain your reasoning:** _______________________________________________

---

## 📋 Answer Sheet

Mark your answers:

```
Section 1: Pattern Identification
1.  [  ]    6.  [  ]    11. [  ]
2.  [  ]    7.  [  ]    12. [  ]
3.  [  ]    8.  [  ]    13. [  ]
4.  [  ]    9.  [  ]    14. [  ]
5.  [  ]    10. [  ]    15. [  ]

Section 2: Code Recognition
16. [  ]    21. [  ]    26. [  ]
17. [  ]    22. [  ]    27. [  ]
18. [  ]    23. [  ]    28. [  ]
19. [  ]    24. [  ]    29. [  ]
20. [  ]    25. [  ]    30. [  ]

Section 3: Scenario Application
31. [  ]    36. [  ]    41. [  ]    46. [  ]
32. [  ]    37. [  ]    42. [  ]    47. [  ]
33. [  ]    38. [  ]    43. [  ]    48. [  ]
34. [  ]    39. [  ]    44. [  ]    49. [  ]
35. [  ]    40. [  ]    45. [  ]    50. [  ]
```

**Score:** _____ / 50

**Check answers in:** `answers/design-patterns-answers.md`

---

<p align="center">
  <b>Good luck! 🍀</b>
</p>
