package models;

import enums.TransactionType;
import enums.TransactionStatus;
import java.util.Date;
import java.util.UUID;

/**
 * Transaction.java - Represents a single ATM transaction.
 * 
 * DESIGN PATTERN: Command Pattern
 * - Encapsulates transaction as an object
 * - execute() method performs the action
 * - Can be logged, undone (in v2)
 * 
 * INTERVIEW TIP: Discuss idempotency for financial transactions.
 */
public class Transaction {
    private final String transactionId;
    private final TransactionType type;
    private final double amount;
    private final Date timestamp;
    private TransactionStatus status;
    private final Account account;

    public Transaction(TransactionType type, double amount, Account account) {
        this.transactionId = UUID.randomUUID().toString().substring(0, 8);
        this.type = type;
        this.amount = amount;
        this.timestamp = new Date();
        this.status = TransactionStatus.PENDING;
        this.account = account;
    }

    /**
     * Execute the transaction.
     * 
     * PATTERN: Command pattern - encapsulate action as object.
     * 
     * @return true if transaction succeeded
     */
    public boolean execute() {
        boolean success = false;

        switch (type) {
            case BALANCE_INQUIRY:
                System.out.printf("Current Balance: $%.2f%n", account.getBalance());
                success = true;
                break;
            case WITHDRAWAL:
                success = account.withdraw(amount);
                if (success) {
                    System.out.printf("Withdrawn: $%.2f%n", amount);
                }
                break;
            case DEPOSIT:
                success = account.deposit(amount);
                if (success) {
                    System.out.printf("Deposited: $%.2f%n", amount);
                }
                break;
        }

        status = success ? TransactionStatus.COMPLETED : TransactionStatus.FAILED;
        return success;
    }

    public String getTransactionId() {
        return transactionId;
    }

    public TransactionType getType() {
        return type;
    }

    public TransactionStatus getStatus() {
        return status;
    }

    public Date getTimestamp() {
        return timestamp;
    }

    @Override
    public String toString() {
        return String.format("[%s] %s: $%.2f - %s",
                transactionId, type, amount, status);
    }
}
