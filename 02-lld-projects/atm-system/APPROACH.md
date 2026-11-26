# Design Approach for ATM System

## Step 1: Identify Core Entities

From the problem statement, we identify these main entities:

| Entity | Description |
|--------|-------------|
| **ATM** | The physical machine, manages sessions and cash |
| **Card** | Bank card with card number, holder information |
| **Account** | Bank account with balance, account type |
| **User** | Customer using the ATM |
| **Transaction** | Individual banking operation |
| **CashDispenser** | Component that dispenses cash |
| **CardReader** | Component that reads/ejects cards |

## Step 2: Define Relationships

```
ATM "1" *-- "1" CardReader : contains
ATM "1" *-- "1" CashDispenser : contains
ATM "1" -- "0..1" Session : current_session
Session "1" -- "1" Card : uses
Card "1" -- "1" User : belongs_to
User "1" -- "*" Account : owns
Account "1" -- "*" Transaction : has_history
```

### Composition vs Association:
- **Composition**: ATM contains CardReader and CashDispenser (physical components)
- **Association**: Session references Card and Account (logical relationship)

## Step 3: Choose Design Patterns

### 3.1 State Pattern (ATM States)
The ATM transitions between states:
- **IdleState**: Waiting for card
- **HasCardState**: Card inserted, awaiting PIN
- **AuthenticatedState**: User authenticated, can perform transactions
- **TransactionState**: Processing a transaction

```
IdleState -> HasCardState -> AuthenticatedState
                  |                   |
                  v                   v
            (Invalid PIN)       TransactionState
```

### 3.2 Command Pattern (Transactions)
Each transaction type is a command:
- `BalanceInquiryCommand`
- `WithdrawCommand`
- `DepositCommand`
- `TransferCommand`
- `ChangePinCommand`

Benefits:
- Encapsulates transaction logic
- Supports undo/rollback
- Easy to add new transaction types

### 3.3 Strategy Pattern (Cash Dispensing)
Different algorithms for cash dispensing:
- `MinimumBillsStrategy`: Use fewest bills possible
- `PreferLargeStrategy`: Prefer larger denominations
- `BalancedStrategy`: Balance between denominations

### 3.4 Singleton Pattern (Bank Service)
Bank communication should be centralized:
- Single connection to bank server
- Thread-safe access to bank operations

## Step 4: Design Classes

### 4.1 ATM (Core Class)
**Responsibilities**: Manage ATM state, coordinate components
**Attributes**:
- `id`: String
- `location`: String
- `state`: ATMState
- `cardReader`: CardReader
- `cashDispenser`: CashDispenser

**Methods**:
- `insertCard(card)`: Begin session
- `authenticatePin(pin)`: Verify PIN
- `selectTransaction(type)`: Choose transaction
- `ejectCard()`: End session

### 4.2 Account
**Responsibilities**: Store balance, perform account operations
**Attributes**:
- `accountNumber`: String
- `accountType`: AccountType (CHECKING, SAVINGS)
- `balance`: double
- `pin`: String (hashed)
- `dailyWithdrawalLimit`: double

**Methods**:
- `getBalance()`: Return current balance
- `withdraw(amount)`: Deduct from balance
- `deposit(amount)`: Add to balance
- `validatePin(pin)`: Verify PIN

### 4.3 Transaction
**Responsibilities**: Record transaction details
**Attributes**:
- `transactionId`: String
- `type`: TransactionType
- `amount`: double
- `timestamp`: DateTime
- `status`: TransactionStatus
- `account`: Account

**Methods**:
- `execute()`: Perform transaction
- `rollback()`: Undo transaction

### 4.4 CashDispenser
**Responsibilities**: Manage and dispense cash
**Attributes**:
- `cashInventory`: Map<Denomination, Integer>
- `dispensingStrategy`: DispensingStrategy

**Methods**:
- `dispenseCash(amount)`: Calculate and dispense bills
- `hasSufficientCash(amount)`: Check availability
- `addCash(denomination, count)`: Refill ATM

## Step 5: Handle Edge Cases

### 5.1 Authentication Failures
```java
if (pinAttempts >= MAX_ATTEMPTS) {
    card.lock();
    return AuthResult.CARD_LOCKED;
}
```

### 5.2 Insufficient Balance
```java
if (amount > account.getBalance()) {
    throw new InsufficientBalanceException(amount, balance);
}
```

### 5.3 ATM Cash Shortage
```java
if (!cashDispenser.hasSufficientCash(amount)) {
    throw new InsufficientCashException("ATM cannot dispense this amount");
}
```

### 5.4 Daily Withdrawal Limit
```java
if (dailyWithdrawn + amount > DAILY_LIMIT) {
    throw new LimitExceededException("Daily withdrawal limit exceeded");
}
```

### 5.5 Session Timeout
```java
if (System.currentTimeMillis() - lastActivity > SESSION_TIMEOUT) {
    ejectCard();
    resetState();
}
```

## Step 6: Optimization Opportunities

### 6.1 Thread Safety (v3)
```java
// Synchronized access to account balance
private final ReentrantLock balanceLock = new ReentrantLock();

public void withdraw(double amount) {
    balanceLock.lock();
    try {
        // perform withdrawal
    } finally {
        balanceLock.unlock();
    }
}
```

### 6.2 Cash Dispensing Optimization
Use greedy algorithm with backtracking for optimal bill combinations.

### 6.3 Connection Pooling
Maintain pool of bank connections for concurrent transactions.

### 6.4 Caching
Cache frequently accessed data:
- Account balances (with TTL)
- Daily transaction totals

### 6.5 Audit Logging
```java
// Async logging for performance
auditLogger.logAsync(new TransactionEvent(transaction));
```

## Version Progression

### v1-basic
- Single account type
- Basic withdraw/deposit/balance
- Simple PIN authentication
- Single-threaded

### v2-extended
- Multiple account types
- Fund transfers
- Transaction history
- PIN change
- Command pattern for transactions

### v3-optimized
- Thread-safe operations
- Concurrent transaction handling
- Optimized cash dispensing
- Session management
- Comprehensive error handling
