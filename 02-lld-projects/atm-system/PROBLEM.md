# ATM System

## Problem Statement

Design an Automated Teller Machine (ATM) system that allows customers to perform banking transactions such as checking balance, withdrawing cash, depositing money, and transferring funds between accounts.

## Functional Requirements

1. **User Authentication**: Authenticate users using a card number and PIN
2. **Balance Inquiry**: Allow users to check their account balance
3. **Cash Withdrawal**: Allow users to withdraw cash from their account
4. **Cash Deposit**: Allow users to deposit cash into their account
5. **PIN Change**: Allow users to change their PIN
6. **Transaction History**: Display recent transaction history
7. **Fund Transfer**: Transfer funds between accounts (v2+)
8. **Multiple Account Types**: Support checking and savings accounts

## Non-Functional Requirements

1. **Security**: PIN should be encrypted, limited authentication attempts
2. **Availability**: System should be highly available
3. **Performance**: Transactions should complete within seconds
4. **Concurrency**: Multiple ATMs should be able to process transactions simultaneously
5. **Audit Trail**: All transactions must be logged

## Constraints & Assumptions

1. Each ATM has a finite amount of cash (denominations: $100, $50, $20, $10)
2. Maximum withdrawal limit per transaction: $1000
3. Daily withdrawal limit: $3000
4. PIN is 4-digit numeric
5. Maximum 3 incorrect PIN attempts before card is locked
6. Session timeout after 2 minutes of inactivity

## Clarifying Questions for Interview

1. **Q: Should we support multiple currencies?**
   A: No, assume single currency (USD) for simplicity.

2. **Q: How should cash dispensing work?**
   A: Dispense minimum number of bills, prefer larger denominations.

3. **Q: Should we handle network failures?**
   A: Yes, in v3 we handle bank communication failures gracefully.

4. **Q: What about account types?**
   A: Support both checking and savings accounts.

## Sample Interactions

```
=== Welcome to ATM ===
Please insert your card...
Card inserted: XXXX-XXXX-XXXX-1234

Enter PIN: ****
Authenticating... Success!

Select an option:
1. Balance Inquiry
2. Cash Withdrawal
3. Cash Deposit
4. Transfer Funds
5. Change PIN
6. Transaction History
7. Exit

Choice: 2

=== Cash Withdrawal ===
Available balance: $5,250.00
Enter amount to withdraw: $200

Dispensing cash...
- 2 x $100 bills

Remaining balance: $5,050.00

Would you like another transaction? (Y/N): N

Thank you for using our ATM. Goodbye!
```
