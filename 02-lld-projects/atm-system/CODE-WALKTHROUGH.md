# Code Walkthrough: ATM System

## Overview

Transaction processing with state machine and security.

---

## State Machine

```
┌─────────────┐
│    IDLE     │ ←─────────────────────┐
└──────┬──────┘                       │
       │ insertCard                   │
       ▼                              │
┌─────────────────┐                   │
│  CARD_INSERTED  │                   │
└──────┬──────────┘                   │
       │ enterPIN                     │
       ▼                              │
┌─────────────────┐     invalid       │
│  AUTHENTICATING │ ─────────────────→│
└──────┬──────────┘                   │
       │ success                      │
       ▼                              │
┌─────────────────┐                   │
│  SELECT_ACTION  │                   │
└──────┬──────────┘                   │
       │ withdraw/deposit/balance     │
       ▼                              │
┌─────────────────┐                   │
│  PROCESSING     │                   │
└──────┬──────────┘                   │
       │ complete                     │
       ▼                              │
┌─────────────────┐     eject card    │
│  TRANSACTION_   │ ──────────────────┘
│  COMPLETE       │
└─────────────────┘
```

---

## Key Classes

```java
class ATM {
    ATMState state;
    CashDispenser dispenser;
    CardReader cardReader;
    BankingService bankService;
}

interface ATMState {
    void insertCard(Card card);
    void enterPIN(String pin);
    void selectTransaction(TransactionType type);
    void withdraw(double amount);
    void deposit(double amount);
    void cancel();
}
```

---

## Interview Questions

### 1. "How to handle insufficient cash?"

```java
class CashDispenser {
    Map<Denomination, Integer> bills;
    
    boolean canDispense(double amount) {
        return calculateBills(amount) != null;
    }
}
```

### 2. "How to prevent card theft?"

- Swallow card after 3 failed PINs
- Session timeout
- Encrypt PIN transmission

### 3. "How to maintain transaction logs?"

```java
class TransactionLog {
    String transactionId;
    Card card;
    TransactionType type;
    double amount;
    LocalDateTime timestamp;
    TransactionStatus status;
}
```

---

## Design Patterns

| Pattern | Usage |
|---------|-------|
| **State** | ATM states |
| **Command** | Transaction commands |
| **Chain of Responsibility** | Transaction validation |
