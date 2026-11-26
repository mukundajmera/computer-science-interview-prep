# Decorator Pattern - Theory

## 🎯 Problem

You need to add features to objects, but:
- Creating a subclass for each combination leads to class explosion
- Features need to be added/removed dynamically
- You want to follow Open/Closed Principle

### Example: Coffee Shop

```
Plain Coffee
Coffee + Milk
Coffee + Milk + Sugar
Coffee + Milk + Sugar + Whip
Coffee + Sugar (no milk)
...

With inheritance: 2^n classes for n options!
With decorator: n+1 classes
```

---

## 💡 Solution

1. Create a common interface for components and decorators
2. Decorators wrap components and add behavior
3. Decorators delegate to wrapped component
4. Stack decorators for combined behaviors

```java
// Stack decorators
Beverage coffee = new Espresso();                    // $1.99
coffee = new MilkDecorator(coffee);                  // +$0.50
coffee = new SugarDecorator(coffee);                 // +$0.25
coffee = new WhipDecorator(coffee);                  // +$0.75
System.out.println(coffee.cost());                   // $3.49
```

---

## 🎯 Interview Questions

### Q1: "How is Decorator different from Inheritance?"

**Answer**:
| Decorator | Inheritance |
|-----------|-------------|
| Runtime composition | Compile-time extension |
| Can add/remove dynamically | Fixed at compile time |
| Single responsibility | Often mixed responsibilities |
| Transparent to client | Client knows specific class |

"Decorator follows 'composition over inheritance' - more flexible but slightly more complex."

### Q2: "When would you NOT use Decorator?"

**Answer**:
"I'd avoid Decorator when:
1. **Order matters**: If decoration order causes issues
2. **Simple cases**: Only 1-2 variations - subclassing is simpler
3. **Identity checks**: `instanceof` checks fail (wrapped object)
4. **Performance critical**: Each decorator adds method call overhead"

### Q3: "How does java.io use Decorator pattern?"

**Answer**:
```java
// Component: InputStream
// Decorators: BufferedInputStream, DataInputStream, etc.

InputStream file = new FileInputStream("data.txt");
InputStream buffered = new BufferedInputStream(file);
DataInputStream data = new DataInputStream(buffered);

int value = data.readInt();  // Uses all three layers
```

"Each wrapper adds functionality:
- FileInputStream: Read bytes from file
- BufferedInputStream: Add buffering
- DataInputStream: Read primitive types"

### Q4: "Decorator vs Strategy - when to use each?"

**Answer**:
| Decorator | Strategy |
|-----------|----------|
| Wraps and enhances | Replaces algorithm |
| Multiple can stack | One at a time |
| Same interface | May have different interface |
| Adds behavior | Changes behavior |

"Use Decorator to add features, Strategy to swap implementations."

### Q5: "How would you implement logging as a decorator?"

**Answer**:
```java
interface Service {
    String process(String input);
}

class LoggingDecorator implements Service {
    private Service wrapped;
    
    public String process(String input) {
        log("Input: " + input);
        String result = wrapped.process(input);
        log("Output: " + result);
        return result;
    }
}

// Usage
Service service = new LoggingDecorator(new RealService());
```

---

## ⚠️ Common Pitfalls

1. **Too many small classes**: Can become hard to track all decorators
2. **Order dependency**: Some decorators must come before others
3. **Type identity lost**: `obj instanceof ConcreteClass` fails
4. **Initialization complexity**: Creating decorated object can be verbose

---

## 📝 Open/Closed Principle

Decorator is a perfect example of Open/Closed:
- **Open for extension**: Add new decorators without changing existing code
- **Closed for modification**: Existing decorators and components unchanged

```java
// Adding new feature - just create new decorator
class ExtraFoamDecorator extends BeverageDecorator {
    // No changes to Espresso, MilkDecorator, etc.
}
```

---

## 🔗 Cross-References

- **LLD Projects**: Notification systems, file processing
- **Related Patterns**: Composite, Strategy, Proxy
- **Theory**: Open/Closed Principle

---

## Interview Lens

- Use when optional runtime behavior needs layering without subclass explosion.
- Call out ordering sensitivity if decorators depend on sequence.
- Compare quickly against Strategy (swap behavior) and Facade (simplify API).
