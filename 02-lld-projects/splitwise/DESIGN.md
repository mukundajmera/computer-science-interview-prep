# Design for Splitwise

Complete class design with diagrams and key decisions.

---

## Mermaid Class Diagram

```mermaid
classDiagram
    class ExpenseManager {
        -Map~String, User~ users
        -List~Expense~ expenses
        -Map~String, Group~ groups
        +addUser(User) void
        +addExpense(Expense) void
        +getBalance(String) Map~String, Double~
        +showBalances() void
        +simplifyDebts() List~Transaction~
    }

    class User {
        -String id
        -String name
        -String email
        -String phone
        +getId() String
        +getName() String
        +getEmail() String
    }

    class Group {
        -String id
        -String name
        -List~User~ members
        -List~Expense~ expenses
        +addMember(User) void
        +removeMember(String) void
        +getMembers() List~User~
        +addExpense(Expense) void
    }

    class Expense {
        -String id
        -String description
        -double amount
        -User paidBy
        -List~Split~ splits
        -ExpenseType expenseType
        -LocalDateTime createdAt
        +validate() boolean
        +getSplits() List~Split~
        +getAmount() double
    }

    class Split {
        <<abstract>>
        -User user
        +getUser() User
        +getAmount()* double
    }

    class EqualSplit {
        -double totalAmount
        -int numParticipants
        +getAmount() double
    }

    class ExactSplit {
        -double amount
        +getAmount() double
    }

    class PercentageSplit {
        -double percentage
        -double totalAmount
        +getAmount() double
    }

    class Balance {
        -User fromUser
        -User toUser
        -double amount
        +getFromUser() User
        +getToUser() User
        +getAmount() double
    }

    class Settlement {
        -String id
        -User payer
        -User payee
        -double amount
        -LocalDateTime settledAt
        +execute() void
    }

    class ExpenseType {
        <<enumeration>>
        EQUAL
        EXACT
        PERCENTAGE
    }

    ExpenseManager "1" --> "n" User : manages
    ExpenseManager "1" --> "n" Expense : tracks
    ExpenseManager "1" --> "n" Group : contains
    Group "1" --> "n" User : has_members
    Group "1" --> "n" Expense : has
    Expense "1" --> "1" User : paid_by
    Expense "1" *-- "n" Split : contains
    Split <|-- EqualSplit
    Split <|-- ExactSplit
    Split <|-- PercentageSplit
    Split --> User : owes
```

## Entity-Relationship Diagram

```mermaid
erDiagram
    USER ||--o{ GROUP_MEMBER : belongs_to
    GROUP ||--o{ GROUP_MEMBER : has
    USER ||--o{ EXPENSE : pays
    GROUP ||--o{ EXPENSE : has
    EXPENSE ||--o{ EXPENSE_SPLIT : splits_into
    USER ||--o{ EXPENSE_SPLIT : owes
    USER ||--o{ BALANCE : owes_to
    USER ||--o{ BALANCE : owed_by
    BALANCE ||--o{ SETTLEMENT : settled_by

    USER {
        string user_id PK
        string name
        string email UK
        string phone
        timestamp created_at
    }

    GROUP {
        string group_id PK
        string name
        string description
        string created_by FK
        timestamp created_at
    }

    GROUP_MEMBER {
        string member_id PK
        string group_id FK
        string user_id FK
        timestamp joined_at
    }

    EXPENSE {
        string expense_id PK
        string group_id FK
        string paid_by FK
        string description
        decimal amount
        string split_type
        timestamp created_at
    }

    EXPENSE_SPLIT {
        string split_id PK
        string expense_id FK
        string user_id FK
        decimal amount
        decimal percentage
    }

    BALANCE {
        string balance_id PK
        string from_user FK
        string to_user FK
        string group_id FK
        decimal amount
        timestamp updated_at
    }

    SETTLEMENT {
        string settlement_id PK
        string balance_id FK
        string payer_id FK
        string payee_id FK
        decimal amount
        timestamp settled_at
    }
```

**Schema Notes:**
- `EXPENSE_SPLIT` stores each user's share of an expense
- `BALANCE` tracks net amounts owed between user pairs
- `SETTLEMENT` records when debts are paid off
- Group expenses vs individual expenses both supported

---

## Class Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                        ExpenseManager                               │
├─────────────────────────────────────────────────────────────────────┤
│ - users: Map<String, User>                                          │
│ - expenses: List<Expense>                                           │
│ - groups: Map<String, Group>                                        │
├─────────────────────────────────────────────────────────────────────┤
│ + addUser(User): void                                               │
│ + addExpense(Expense): void                                         │
│ + getBalance(userId): Map<String, Double>                           │
│ + showBalances(): void                                              │
│ + simplifyDebts(): List<Transaction>                                │
└───────────────────────────────┬─────────────────────────────────────┘
                                │ manages
          ┌─────────────────────┼─────────────────────┐
          ▼                     ▼                     ▼
┌───────────────────┐  ┌───────────────────┐  ┌───────────────────┐
│       User        │  │     Expense       │  │      Group        │
├───────────────────┤  ├───────────────────┤  ├───────────────────┤
│ - id: String      │  │ - id: String      │  │ - id: String      │
│ - name: String    │  │ - description     │  │ - name: String    │
│ - email: String   │  │ - amount: double  │  │ - members: User[] │
├───────────────────┤  │ - paidBy: User    │  ├───────────────────┤
│ + getId()         │  │ - splits: Split[] │  │ + addMember()     │
└───────────────────┘  │ - splitType       │  │ + getMembers()    │
                       ├───────────────────┤  └───────────────────┘
                       │ + validate()      │
                       │ + getSplits()     │
                       └────────┬──────────┘
                                │ contains
                                ▼
         ┌─────────────────────────────────────────────────┐
         │              Split <<abstract>>                 │
         ├─────────────────────────────────────────────────┤
         │ - user: User                                    │
         ├─────────────────────────────────────────────────┤
         │ + getUser(): User                               │
         │ + getAmount(): double <<abstract>>              │
         └──────────────────────┬──────────────────────────┘
                                │
          ┌─────────────────────┼─────────────────────┐
          ▼                     ▼                     ▼
┌───────────────────┐  ┌───────────────────┐  ┌───────────────────┐
│    EqualSplit     │  │    ExactSplit     │  │ PercentageSplit   │
├───────────────────┤  ├───────────────────┤  ├───────────────────┤
│ - totalAmount     │  │ - amount: double  │  │ - percentage: %   │
│ - numParticipants │  ├───────────────────┤  │ - totalAmount     │
├───────────────────┤  │ + getAmount()     │  ├───────────────────┤
│ + getAmount()     │  └───────────────────┘  │ + getAmount()     │
└───────────────────┘                         └───────────────────┘
```

---

## Split Calculation

### Equal Split
```
amount = totalAmount / numberOfParticipants
// Handle rounding: give extra cents to first participant
```

### Exact Split
```
// User specifies exact amount
// Validation: sum of splits == totalAmount
```

### Percentage Split
```
amount = totalAmount * (percentage / 100)
// Validation: sum of percentages == 100
```

---

## Balance Calculation Algorithm

```
For each expense:
    payer = expense.getPaidBy()
    for each split in expense.getSplits():
        borrower = split.getUser()
        amount = split.getAmount()
        
        if borrower != payer:
            balances[borrower][payer] += amount
            balances[payer][borrower] -= amount  // Can go negative

// Simplify: if A owes B $10 and B owes A $3, net is A owes B $7
```

---

## Debt Simplification Algorithm (v3)

```
simplifyDebts():
    1. Calculate net balance for each user
       netBalance[user] = (money owed to user) - (money user owes)
    
    2. Separate into creditors (positive) and debtors (negative)
    
    3. Greedy matching:
       While there are creditors and debtors:
           Find max creditor and max debtor
           amount = min(creditor.balance, abs(debtor.balance))
           Create transaction: debtor pays creditor `amount`
           Update balances
    
    Time: O(n log n) for sorting, O(n) for matching
    
    Note: This is a heuristic. Optimal solution is NP-hard.
```

---

## Key Design Decisions

### Decision 1: Strategy Pattern for Splits
**Rationale**: 
- Different calculation logic per split type
- Easy to add new split types
- Clean separation of concerns

### Decision 2: Balance as Derived Data
**Rationale**:
- Calculate on-demand from expense history
- No sync issues between expenses and balances
- Trade-off: O(n) calculation vs O(1) lookup with caching

### Decision 3: Rounding Strategy
**Rationale**:
- Use BigDecimal/Decimal for accuracy
- Round to 2 decimal places
- Assign remaining cents to first participant

---

## Complexity Analysis

| Operation | Complexity | Notes |
|-----------|------------|-------|
| Add expense | O(k) | k = participants |
| Get balance for user | O(e * k) | e = expenses |
| Show all balances | O(n² + e*k) | n = users |
| Simplify debts | O(n log n) | Greedy approach |

---

## Extension Points

| Feature | Implementation |
|---------|----------------|
| Multiple currencies | Add currency to Amount class |
| Recurring expenses | Schedule with cron-like pattern |
| Expense categories | Add category field |
| Attachments | Link to file storage |
| Notifications | Observer pattern |
