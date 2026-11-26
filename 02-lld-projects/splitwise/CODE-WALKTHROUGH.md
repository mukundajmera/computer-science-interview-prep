# Code Walkthrough: Splitwise

## Overview

Expense splitting app - common interview question for fintech roles.

---

## File Structure

```
java/v1-basic/
├── User.java           # User entity
├── Expense.java        # Expense with split logic
├── Split.java          # Individual split record
├── ExpenseManager.java # Core business logic
└── SplitwiseDemo.java  # Demo

python/v1-basic/
├── user.py
├── expense.py
├── split.py
├── expense_manager.py
└── splitwise_demo.py
```

---

## Core Concepts

### Split Types

| Type | Description | Example |
|------|-------------|---------|
| EQUAL | Divide equally | $100 / 4 = $25 each |
| EXACT | Specify amounts | A:$50, B:$30, C:$20 |
| PERCENT | Percentage based | A:50%, B:30%, C:20% |

### Balance Calculation

```
User A pays $100 for A, B, C (equal split)
- A paid: $100
- A owes: $33.33 (their share)
- A is owed: $66.67 (B's + C's share)

Net: B owes A $33.33, C owes A $33.33
```

---

## Key Classes

```java
class ExpenseManager {
    Map<String, User> users;
    Map<String, Map<String, Double>> balances; // who owes whom
    
    void addExpense(Expense expense) { ... }
    Map<String, Double> getBalances(String userId) { ... }
    List<String> simplifyDebts() { ... }
}
```

---

## Interview Questions

### 1. "How do you calculate balances?"

Maintain pairwise balance map:
```java
// balances[A][B] = positive means B owes A
void updateBalance(String payer, String owes, double amount) {
    balances.get(payer).merge(owes, amount, Double::sum);
    balances.get(owes).merge(payer, -amount, Double::sum);
}
```

### 2. "How to simplify debts?"

**Problem:** A→B→C can become A→C directly

**Algorithm:** 
1. Calculate net balance per user
2. Match creditors with debtors
3. Minimize transactions (greedy or optimal)

```java
// Greedy approach
while (!debtors.isEmpty()) {
    User debtor = getMaxDebtor();
    User creditor = getMaxCreditor();
    settle(debtor, creditor, min(debt, credit));
}
```

### 3. "How to handle groups?"

```java
class Group {
    String id;
    List<User> members;
    List<Expense> expenses;
    
    Map<String, Double> getGroupBalances() { ... }
}
```

### 4. "How to handle currency conversion?"

Add Currency to Expense, convert at settlement:
```java
class Expense {
    Currency currency;
    double amount;
}
```

---

## Design Patterns

| Pattern | Usage |
|---------|-------|
| **Strategy** | Split calculation (EQUAL, EXACT, PERCENT) |
| **Observer** | Notify users of new expenses |
| **Singleton** | ExpenseManager as central controller |

---

## Complexity

| Operation | Time | Space |
|-----------|------|-------|
| addExpense | O(U) | O(1) |
| getBalances | O(U) | O(U) |
| simplifyDebts | O(U²) or O(U log U) | O(U) |

Where U = number of users
