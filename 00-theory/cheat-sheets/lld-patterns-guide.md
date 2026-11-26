# LLD Patterns Quick Reference

## Which Pattern for Which Problem?

| Problem Type | Primary Pattern | Secondary | Example |
|--------------|-----------------|-----------|---------|
| Single instance needed | **Singleton** | - | DB Connection, Logger |
| Object creation varies | **Factory Method** | Abstract Factory | Notification types |
| Complex object construction | **Builder** | - | HTTP Request, Config |
| Clone existing object | **Prototype** | - | Document templates |
| Families of objects | **Abstract Factory** | - | UI themes |

---

## LLD Problem → Pattern Mapping

| LLD Problem | Core Patterns |
|-------------|---------------|
| **Parking Lot** | Singleton, Strategy (pricing), Factory (vehicle) |
| **Elevator System** | Singleton, State, Strategy (dispatch) |
| **LRU Cache** | - (DS-focused: HashMap + DLL) |
| **Rate Limiter** | Strategy (algorithm), Singleton |
| **Vending Machine** | State, Singleton |
| **Chess** | Factory (pieces), Strategy (move validation) |
| **Splitwise** | Strategy (split types), Observer |
| **Movie Booking** | Singleton, Strategy (pricing), Observer |
| **ATM** | State, Chain of Responsibility, Command |
| **Hotel/Library** | Singleton, Observer, Strategy |

---

## Pattern Recognition Tips

### Use Singleton When:
- ✅ Single DB connection pool
- ✅ Configuration manager
- ✅ Central controller (ParkingLot, ElevatorSystem)
- ❌ NOT for stateless services

### Use Factory When:
- ✅ Multiple implementations of interface
- ✅ Object type decided at runtime
- ✅ Creating vehicles, notifications, payments

### Use Strategy When:
- ✅ Multiple algorithms for same task
- ✅ Pricing strategies
- ✅ Sorting/scheduling algorithms

### Use State When:
- ✅ Object behavior changes with state
- ✅ Vending machine, ATM, Elevator
- ✅ Clear state transitions

### Use Observer When:
- ✅ Notify multiple objects of changes
- ✅ Booking confirmations
- ✅ Stock alerts

---

## Quick Decision Tree

```
Need single instance?
  └─ YES → Singleton
  
Object creation varies?
  └─ YES → Factory
  
Behavior changes with state?
  └─ YES → State Pattern
  
Multiple algorithms?
  └─ YES → Strategy
  
Notify on changes?
  └─ YES → Observer
```

---

## Interview Priority Lane

Use this order when time is tight:
1. Strategy
2. Factory Method
3. State
4. Observer
5. Builder
6. Decorator
7. Facade
8. Singleton (only when truly required)

---

## Common Misuse Signals

- Singleton chosen for convenience rather than global consistency requirement.
- Builder introduced for objects with only one or two optional fields.
- Decorator used when simple compile-time composition would suffice.
- State/Strategy confusion: no state transition model, only algorithm swap.
