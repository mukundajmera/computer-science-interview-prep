# Splitwise

## Problem Statement

Design an expense sharing application (like Splitwise) that allows users to add expenses and split them among group members using various splitting strategies.

---

## Functional Requirements

1. **User Management**: Add and manage users
2. **Add Expense**: Record expenses with payer and participants
3. **Split Types**: 
   - Equal split (divide equally)
   - Exact split (specify exact amounts)
   - Percentage split (specify percentages)
4. **Balance Calculation**: Calculate who owes whom
5. **Group Expenses**: Create groups for recurring splits
6. **Settle Up**: Record payments between users
7. **Show Balances**: Display all outstanding balances
8. **Simplify Debts**: Minimize number of transactions

---

## Non-Functional Requirements

1. **Data Consistency**: Balances must always be accurate
2. **Scalability**: Support many users and expenses
3. **Concurrency**: Handle simultaneous expense additions (v3)
4. **Audit Trail**: Track all expenses and payments

---

## Constraints & Assumptions

- All amounts in same currency
- No interest on balances
- Users are pre-registered
- Amounts rounded to 2 decimal places
- Percentages must sum to 100%
- Exact splits must sum to total expense

---

## Sample Interactions

```
1. Add users: Alice, Bob, Charlie
2. Alice pays $300 for dinner (split equally)
   - Bob owes Alice $100
   - Charlie owes Alice $100
3. Bob pays $150 for movie (split: Alice 50%, Bob 30%, Charlie 20%)
   - Alice owes Bob $75
   - Charlie owes Bob $30
4. Show balances:
   - Bob owes Alice $25 (100-75)
   - Charlie owes Alice $100
   - Charlie owes Bob $30
5. Simplify:
   - Charlie pays Alice $100
   - Charlie pays Bob $30
   - Bob pays Alice $25
```

---

## Clarifying Questions to Ask

1. "What split types need to be supported?"
2. "Do we need groups or just individual splits?"
3. "Should we track expense categories?"
4. "Do we need to simplify debts (minimize transactions)?"
5. "Is there a notion of currency?"
6. "Should we support recurring expenses?"
7. "How to handle rounding differences?"
8. "Do we need expense history/audit?"

---

## Entities to Identify

| Entity | Responsibility |
|--------|---------------|
| User | Person who can pay or owe money |
| Expense | A single expense with payer and splits |
| Split | How much each user owes for an expense |
| Group | Collection of users for shared expenses |
| Balance | Amount owed between two users |
| ExpenseManager | Main service to manage expenses |

---

## Split Strategies

| Strategy | Description |
|----------|-------------|
| Equal | Divide total equally among participants |
| Exact | Specify exact amount for each participant |
| Percentage | Specify percentage for each participant |

---

## Version Roadmap

| Version | Features |
|---------|----------|
| v1-basic | Users, expenses, equal split, balance calculation |
| v2-extended | Exact/percentage splits, groups, simplify debts |
| v3-optimized | Thread-safe, optimized settlement algorithm |
