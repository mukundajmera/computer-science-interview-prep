# Design for ATM System

## Mermaid Class Diagram

```mermaid
classDiagram
    class ATM {
        -String atmId
        -String location
        -ATMState currentState
        -CardReader cardReader
        -CashDispenser cashDispenser
        -Session currentSession
        +insertCard(Card) boolean
        +authenticatePin(String) AuthResult
        +executeTransaction(Transaction) TransactionResult
        +ejectCard() void
        +getAvailableCash() Map
    }

    class CardReader {
        -boolean isCardPresent
        -Card currentCard
        +readCard() Card
        +ejectCard() void
        +retainCard() void
    }

    class CashDispenser {
        -Map~Denomination, Integer~ inventory
        -DispensingStrategy strategy
        +dispense(int) Map
        +canDispense(int) boolean
        +addCash(Denomination, int) void
    }

    class Session {
        -Card card
        -Account account
        -LocalDateTime startTime
        +isExpired() boolean
        +getAccount() Account
    }

    class Account {
        -String accountNumber
        -AccountType accountType
        -double balance
        -String pinHash
        -boolean isLocked
        -int failedAttempts
        -double dailyWithdrawn
        +getBalance() double
        +withdraw(double) boolean
        +deposit(double) boolean
        +validatePin(String) boolean
        +canWithdraw(double) boolean
        +lock() void
    }

    class Transaction {
        -String transactionId
        -TransactionType type
        -double amount
        -LocalDateTime timestamp
        -TransactionStatus status
        -Account sourceAccount
        -Account destinationAccount
        +execute() TransactionResult
        +rollback() boolean
        +getDetails() String
    }

    class ATMState {
        <<interface>>
        +insertCard(Card) void
        +ejectCard() void
        +enterPin(String) void
        +selectTransaction(TransactionType) void
        +executeTransaction() void
    }

    class IdleState {
        +insertCard(Card) void
    }

    class HasCardState {
        +enterPin(String) void
        +ejectCard() void
    }

    class AuthenticatedState {
        +selectTransaction(TransactionType) void
        +ejectCard() void
    }

    class TransactionState {
        +executeTransaction() void
        +ejectCard() void
    }

    class DispensingStrategy {
        <<interface>>
        +calculateBills(int, Map) Map
    }

    class MinimumBillsStrategy {
        +calculateBills(int, Map) Map
    }

    class PreferLargeStrategy {
        +calculateBills(int, Map) Map
    }

    class AccountType {
        <<enumeration>>
        CHECKING
        SAVINGS
    }

    class TransactionType {
        <<enumeration>>
        BALANCE_INQUIRY
        WITHDRAWAL
        DEPOSIT
        TRANSFER
        PIN_CHANGE
    }

    class TransactionStatus {
        <<enumeration>>
        PENDING
        COMPLETED
        FAILED
        CANCELLED
    }

    ATM *-- CardReader
    ATM *-- CashDispenser
    ATM --> ATMState : has_current
    ATM --> Session : manages
    ATMState <|.. IdleState
    ATMState <|.. HasCardState
    ATMState <|.. AuthenticatedState
    ATMState <|.. TransactionState
    CashDispenser --> DispensingStrategy : uses
    DispensingStrategy <|.. MinimumBillsStrategy
    DispensingStrategy <|.. PreferLargeStrategy
    Session --> Account
    Account "1" --> "n" Transaction : has
```

## Entity-Relationship Diagram

```mermaid
erDiagram
    BANK ||--o{ ATM : owns
    BANK ||--o{ ACCOUNT : manages
    ACCOUNT ||--o{ CARD : has
    ACCOUNT ||--o{ TRANSACTION : performs
    ATM ||--o{ ATM_SESSION : hosts
    ATM_SESSION ||--o{ TRANSACTION : contains

    BANK {
        string bank_id PK
        string name
        string routing_number
    }

    ATM {
        string atm_id PK
        string bank_id FK
        string location
        string status
        timestamp last_serviced
    }

    ACCOUNT {
        string account_number PK
        string bank_id FK
        string account_type
        decimal balance
        string pin_hash
        boolean is_locked
        int failed_attempts
        decimal daily_limit
        decimal daily_withdrawn
    }

    CARD {
        string card_number PK
        string account_number FK
        date expiry_date
        boolean is_active
        string card_type
    }

    ATM_SESSION {
        string session_id PK
        string atm_id FK
        string card_number FK
        timestamp start_time
        timestamp end_time
        string status
    }

    TRANSACTION {
        string transaction_id PK
        string session_id FK
        string source_account FK
        string destination_account FK
        string type
        decimal amount
        timestamp timestamp
        string status
    }
```

**Schema Notes:**
- `ACCOUNT` stores balance and PIN hash with security fields
- `ATM_SESSION` tracks each card insertion session
- `TRANSACTION` logs all operations with rollback support
- Daily limits tracked in `ACCOUNT` for withdrawal restrictions

---

## Class Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              ATM SYSTEM                                      │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   <<enum>>      │     │   <<enum>>      │     │   <<enum>>      │
│ AccountType     │     │ TransactionType │     │ TransactionStatus│
├─────────────────┤     ├─────────────────┤     ├─────────────────┤
│ CHECKING        │     │ BALANCE_INQUIRY │     │ PENDING          │
│ SAVINGS         │     │ WITHDRAWAL      │     │ COMPLETED        │
└─────────────────┘     │ DEPOSIT         │     │ FAILED           │
                        │ TRANSFER        │     │ CANCELLED        │
                        │ PIN_CHANGE      │     └─────────────────┘
                        └─────────────────┘

┌───────────────────────────────────────────────────────────────────────┐
│                                 ATM                                    │
├───────────────────────────────────────────────────────────────────────┤
│ - atmId: String                                                        │
│ - location: String                                                     │
│ - currentState: ATMState                                               │
│ - cardReader: CardReader                                               │
│ - cashDispenser: CashDispenser                                         │
│ - currentSession: Session                                              │
├───────────────────────────────────────────────────────────────────────┤
│ + insertCard(card: Card): boolean                                      │
│ + authenticatePin(pin: String): AuthResult                             │
│ + executeTransaction(transaction: Transaction): TransactionResult      │
│ + ejectCard(): void                                                    │
│ + getAvailableCash(): Map<Denomination, Integer>                       │
└───────────────────────────────────────────────────────────────────────┘
          │                    │                    │
          │ contains           │ contains           │ has
          ▼                    ▼                    ▼
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│   CardReader    │  │  CashDispenser  │  │     Session     │
├─────────────────┤  ├─────────────────┤  ├─────────────────┤
│ - isCardPresent │  │ - inventory     │  │ - card: Card    │
│ - currentCard   │  │ - strategy      │  │ - account       │
├─────────────────┤  ├─────────────────┤  │ - startTime     │
│ + readCard()    │  │ + dispense()    │  ├─────────────────┤
│ + ejectCard()   │  │ + canDispense() │  │ + isExpired()   │
│ + retainCard()  │  │ + addCash()     │  │ + getAccount()  │
└─────────────────┘  └─────────────────┘  └─────────────────┘

┌───────────────────────────────────────────────────────────────────────┐
│                               Account                                  │
├───────────────────────────────────────────────────────────────────────┤
│ - accountNumber: String                                                │
│ - accountType: AccountType                                             │
│ - balance: double                                                      │
│ - pinHash: String                                                      │
│ - isLocked: boolean                                                    │
│ - failedAttempts: int                                                  │
│ - dailyWithdrawn: double                                               │
├───────────────────────────────────────────────────────────────────────┤
│ + getBalance(): double                                                 │
│ + withdraw(amount: double): boolean                                    │
│ + deposit(amount: double): boolean                                     │
│ + validatePin(pin: String): boolean                                    │
│ + canWithdraw(amount: double): boolean                                 │
│ + lock(): void                                                         │
└───────────────────────────────────────────────────────────────────────┘
                              │
                              │ has many
                              ▼
┌───────────────────────────────────────────────────────────────────────┐
│                             Transaction                                │
├───────────────────────────────────────────────────────────────────────┤
│ - transactionId: String                                                │
│ - type: TransactionType                                                │
│ - amount: double                                                       │
│ - timestamp: LocalDateTime                                             │
│ - status: TransactionStatus                                            │
│ - sourceAccount: Account                                               │
│ - destinationAccount: Account (for transfers)                          │
├───────────────────────────────────────────────────────────────────────┤
│ + execute(): TransactionResult                                         │
│ + rollback(): boolean                                                  │
│ + getDetails(): String                                                 │
└───────────────────────────────────────────────────────────────────────┘

┌───────────────────────────────────────────────────────────────────────┐
│                        <<interface>> ATMState                          │
├───────────────────────────────────────────────────────────────────────┤
│ + insertCard(card: Card): void                                         │
│ + ejectCard(): void                                                    │
│ + enterPin(pin: String): void                                          │
│ + selectTransaction(type: TransactionType): void                       │
│ + executeTransaction(): void                                           │
└───────────────────────────────────────────────────────────────────────┘
          △
          │ implements
          │
    ┌─────┴─────┬─────────────┬─────────────┐
    │           │             │             │
┌───────────┐ ┌───────────┐ ┌───────────┐ ┌───────────┐
│ IdleState │ │HasCardState│ │Authenticated│ │Transaction│
│           │ │           │ │   State     │ │   State   │
└───────────┘ └───────────┘ └───────────┘ └───────────┘

┌───────────────────────────────────────────────────────────────────────┐
│                  <<interface>> DispensingStrategy                      │
├───────────────────────────────────────────────────────────────────────┤
│ + calculateBills(amount: int, inventory: Map): Map<Denomination, Int>  │
└───────────────────────────────────────────────────────────────────────┘
          △
          │ implements
          │
    ┌─────┴─────────────────┐
    │                       │
┌───────────────────┐ ┌───────────────────┐
│ MinimumBills      │ │ PreferLarge       │
│ Strategy          │ │ Strategy          │
└───────────────────┘ └───────────────────┘
```

## Core Classes

### ATM
- **Attributes**: atmId, location, currentState, cardReader, cashDispenser, currentSession
- **Methods**: insertCard(), authenticatePin(), executeTransaction(), ejectCard()
- **Patterns Used**: State Pattern (manages ATM states)

### Account
- **Attributes**: accountNumber, accountType, balance, pinHash, isLocked, failedAttempts
- **Methods**: getBalance(), withdraw(), deposit(), validatePin(), canWithdraw()
- **Patterns Used**: None (core domain entity)

### Transaction
- **Attributes**: transactionId, type, amount, timestamp, status, sourceAccount, destinationAccount
- **Methods**: execute(), rollback(), getDetails()
- **Patterns Used**: Command Pattern (each transaction is a command)

### CashDispenser
- **Attributes**: inventory (Map<Denomination, Integer>), strategy (DispensingStrategy)
- **Methods**: dispense(), canDispense(), addCash()
- **Patterns Used**: Strategy Pattern (pluggable dispensing algorithms)

### ATMState (Interface)
- **Implementations**: IdleState, HasCardState, AuthenticatedState, TransactionState
- **Methods**: insertCard(), ejectCard(), enterPin(), selectTransaction()
- **Patterns Used**: State Pattern

## Key Design Decisions

### 1. State Pattern for ATM States
**Decision**: Use State pattern to manage ATM lifecycle
**Rationale**: 
- Clear separation of behavior based on ATM state
- Easy to add new states (e.g., MaintenanceState)
- Prevents invalid operations (can't withdraw without card)
**Trade-off**: More classes, but cleaner code

### 2. Command Pattern for Transactions
**Decision**: Each transaction type is a Command object
**Rationale**:
- Encapsulates transaction logic
- Supports transaction history and rollback
- Easy to add new transaction types
**Trade-off**: Slight overhead for simple operations

### 3. Strategy Pattern for Cash Dispensing
**Decision**: Pluggable algorithm for bill calculation
**Rationale**:
- Different ATMs may have different policies
- Easy to optimize or change algorithm
**Trade-off**: Extra abstraction layer

### 4. PIN Hashing
**Decision**: Store PIN as hash, not plain text
**Rationale**: Security best practice
**Trade-off**: Cannot recover PIN, only reset

### 5. Daily Limit Tracking
**Decision**: Track daily withdrawals per account
**Rationale**: Bank policy compliance
**Trade-off**: Need to reset at midnight (timezone consideration)

## Sequence Diagrams

### Withdrawal Flow
```
User        ATM         State       Account     CashDispenser
 │           │            │            │              │
 │ insertCard│            │            │              │
 │──────────>│            │            │              │
 │           │ insertCard │            │              │
 │           │───────────>│            │              │
 │           │            │ setState   │              │
 │           │            │ (HasCard)  │              │
 │           │            │            │              │
 │ enterPIN  │            │            │              │
 │──────────>│ enterPIN   │            │              │
 │           │───────────>│ validatePin│              │
 │           │            │───────────>│              │
 │           │            │   valid    │              │
 │           │            │<───────────│              │
 │           │ setState   │            │              │
 │           │ (Auth)     │            │              │
 │           │            │            │              │
 │ withdraw  │            │            │              │
 │ $200      │            │            │              │
 │──────────>│ withdraw   │ canWithdraw│              │
 │           │───────────>│───────────>│              │
 │           │            │   true     │ canDispense? │
 │           │            │<───────────│──────────────>
 │           │            │            │    true      │
 │           │            │ withdraw   │<─────────────│
 │           │            │───────────>│   dispense   │
 │           │            │   success  │──────────────>
 │           │<───────────│            │    bills     │
 │  cash     │            │            │              │
 │<──────────│            │            │              │
```

## Complexity Analysis

### Time Complexity
| Operation | Complexity | Notes |
|-----------|------------|-------|
| Balance Inquiry | O(1) | Direct account access |
| Withdrawal | O(D) | D = number of denominations |
| Deposit | O(1) | Simple balance update |
| Transfer | O(1) | Two balance updates |
| Transaction History | O(N) | N = number of transactions |
| PIN Validation | O(1) | Hash comparison |

### Space Complexity
| Component | Complexity | Notes |
|-----------|------------|-------|
| Account | O(T) | T = transaction history size |
| CashDispenser | O(D) | D = denomination types |
| Session | O(1) | Fixed session data |
| Transaction Log | O(N) | N = total transactions |

## Error Handling

### Exception Hierarchy
```
ATMException (base)
├── AuthenticationException
│   ├── InvalidPinException
│   └── CardLockedException
├── TransactionException
│   ├── InsufficientBalanceException
│   ├── InsufficientCashException
│   └── DailyLimitExceededException
├── CardException
│   ├── InvalidCardException
│   └── ExpiredCardException
└── SystemException
    ├── NetworkException
    └── HardwareException
```

## Concurrency Considerations (v3)

### Thread Safety
1. **Account Balance**: Use ReentrantLock for atomic operations
2. **Cash Inventory**: ConcurrentHashMap for thread-safe access
3. **Daily Limit Counter**: AtomicReference for thread-safe updates

### Race Conditions to Handle
1. **Double Withdrawal**: Lock account during transaction
2. **Cash Inventory**: Synchronized dispensing
3. **PIN Attempts**: Atomic increment for failed attempts

```java
// Thread-safe withdrawal
public synchronized boolean withdraw(double amount) {
    if (canWithdraw(amount)) {
        this.balance -= amount;
        this.dailyWithdrawn += amount;
        return true;
    }
    return false;
}
```
