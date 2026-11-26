# Design Approach for Splitwise

A step-by-step thought process for designing the expense sharing system.

---

## Step 1: Identify Core Entities

| Noun | Entity? | Reasoning |
|------|---------|-----------|
| User | ✅ Yes | Person in the system |
| Expense | ✅ Yes | A spending event |
| Split | ✅ Yes | Portion of expense |
| Group | ✅ v2 | Collection of users |
| Balance | ❌ No | Derived from expenses |
| Transaction/Payment | ✅ Yes | Settlement payment |

---

## Step 2: Define Relationships

```
ExpenseManager (1) ──manages──> (n) User
ExpenseManager (1) ──manages──> (n) Expense
Expense (1) ──paid by──> (1) User
Expense (1) ──contains──> (n) Split
Split (n) ──owed by──> (1) User
Group (1) ──contains──> (n) User
```

---

## Step 3: Choose Design Patterns

| Pattern | Apply? | Justification |
|---------|--------|---------------|
| **Strategy** | ✅ Yes | Different split types (equal, exact, %) |
| **Observer** | ✅ v2 | Notify users of new expenses |
| **Factory** | ✅ Yes | Create different split types |
| **Composite** | ✅ v2 | Group hierarchies |

---

## Step 4: Design Classes

### ExpenseManager
- **Attributes**: 
  - `users: Map<String, User>`
  - `expenses: List<Expense>`
  - `balances: Map<String, Map<String, Double>>`
- **Methods**:
  - `addUser(User): void`
  - `addExpense(Expense): void`
  - `getBalance(userId): Map<String, Double>`
  - `showBalances(): void`
  - `settleUp(from, to, amount): void`

### User
- **Attributes**:
  - `id: String`
  - `name: String`
  - `email: String`

### Expense
- **Attributes**:
  - `id: String`
  - `description: String`
  - `amount: double`
  - `paidBy: User`
  - `splits: List<Split>`
  - `splitType: SplitType`

### Split (Abstract)
- **Attributes**:
  - `user: User`
- **Methods**:
  - `getAmount(): double`

### EqualSplit, ExactSplit, PercentageSplit
- Subclasses with specific calculation logic

---

## Step 5: Handle Edge Cases

- Rounding differences in equal splits
- Percentage not summing to 100%
- Exact amounts not summing to total
- User paying for themselves only
- Negative balances (simplification)
- Self-loops in balance graph

---

## Step 6: Optimization Opportunities

### Debt Simplification Algorithm

The problem of minimizing transactions is essentially finding the optimal way to settle a graph of debts.

**Greedy Approach**:
1. Calculate net balance for each user
2. Match users with positive and negative balances
3. Create transactions to settle

**Example**:
- A owes B $10, B owes C $10, C owes A $5
- Net: A: -5, B: 0, C: +5
- Simplified: A pays C $5 (1 transaction instead of 3)

---

## Step 7: Version Progression

### v1-basic (~300 lines)
- User, Expense, EqualSplit
- Basic balance tracking
- Show balances

### v2-extended (~500 lines)
- ExactSplit, PercentageSplit
- Groups
- Simplify debts

### v3-optimized (~700 lines)
- Thread-safe operations
- Optimized graph-based simplification
- Transaction history
