# Interpreter Pattern - Theory & Interview Guide

## 📚 Core Concept

The Interpreter pattern defines a grammar for a simple language and provides an interpreter to parse sentences in that language.

### Key Components

1. **AbstractExpression**: Declares interpret() method
2. **TerminalExpression**: Implements interpret for terminal symbols
3. **NonterminalExpression**: Represents grammar rules, contains other expressions
4. **Context**: Contains global information for interpretation
5. **Client**: Builds the abstract syntax tree and invokes interpret()

## 🎯 Problem It Solves

**Without Interpreter:**
```java
// Hard-coded evaluation logic
if (expression.equals("A AND B")) {
    return a && b;
} else if (expression.equals("A OR B")) {
    return a || b;
}
// Every new expression requires code changes!
```

**With Interpreter:**
```java
Expression exp = new AndExpression(
    new VariableExpression("A"),
    new VariableExpression("B")
);
boolean result = exp.interpret(context);
```

## ✅ When to Use

1. **Simple grammars** that occur frequently
2. **Efficiency not critical** - interpreters can be slow
3. **DSL (Domain Specific Language)** implementation
4. Examples: SQL parsing, regex, math expressions, rules engines

## ❌ When NOT to Use

1. Complex grammars - use parser generators
2. Performance-critical applications
3. Frequently changing grammar

## 🎤 Interview Q&A

### Q1: Real-world examples?

**A:**
- Regular expressions
- SQL WHERE clause evaluation
- Mathematical expression calculators
- Configuration file parsers
- Rules engines (business rules)

### Q2: Why is efficiency a concern?

**A:** Each grammar rule creates a class, and interpretation requires traversing the expression tree. For complex grammars, parsing and interpretation become expensive. Use parser generators (ANTLR, yacc) for complex cases.

### Q3: How does it relate to Composite?

**A:** Interpreter often uses Composite structure:
- TerminalExpression = Leaf
- NonterminalExpression = Composite (contains children)

## 💻 Code Pattern

### Java - Boolean Expression
```java
interface Expression {
    boolean interpret(Map<String, Boolean> context);
}

class VariableExpression implements Expression {
    private String name;
    
    public boolean interpret(Map<String, Boolean> context) {
        return context.get(name);
    }
}

class AndExpression implements Expression {
    private Expression left, right;
    
    public boolean interpret(Map<String, Boolean> context) {
        return left.interpret(context) && right.interpret(context);
    }
}
```

### Python
```python
class Expression(ABC):
    @abstractmethod
    def interpret(self, context: dict) -> bool:
        pass

class VariableExpression(Expression):
    def __init__(self, name: str):
        self.name = name
    
    def interpret(self, context: dict) -> bool:
        return context.get(self.name, False)

class AndExpression(Expression):
    def __init__(self, left: Expression, right: Expression):
        self.left = left
        self.right = right
    
    def interpret(self, context: dict) -> bool:
        return self.left.interpret(context) and self.right.interpret(context)
```

## 🔗 Related Patterns

| Pattern | Relationship |
|---------|-------------|
| **Composite** | Expression tree structure |
| **Visitor** | Can separate operations from expressions |
| **Flyweight** | Share terminal expressions |

---

[← Back to Interpreter](./README.md)
