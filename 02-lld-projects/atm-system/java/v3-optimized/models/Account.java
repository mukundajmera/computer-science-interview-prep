package models;

import enums.AccountType;

/**
 * Account.java - Bank account with balance and PIN management.
 * 
 * DESIGN DECISIONS:
 * - PIN validation with lockout after 3 failed attempts
 * - Immutable account number and type
 * - Thread-safe in v3
 * 
 * INTERVIEW TIP: Discuss security measures like PIN hashing.
 */
public class Account {
    private final String accountNumber;
    private final AccountType accountType;
    private double balance;
    private String pin;
    private boolean isLocked;
    private int failedAttempts;

    private static final int MAX_FAILED_ATTEMPTS = 3;

    public Account(String accountNumber, AccountType accountType, double initialBalance, String pin) {
        this.accountNumber = accountNumber;
        this.accountType = accountType;
        this.balance = initialBalance;
        this.pin = pin;
        this.isLocked = false;
        this.failedAttempts = 0;
    }

    public String getAccountNumber() {
        return accountNumber;
    }

    public AccountType getAccountType() {
        return accountType;
    }

    public double getBalance() {
        return balance;
    }

    public boolean isLocked() {
        return isLocked;
    }

    /**
     * Validate PIN with lockout protection.
     * 
     * SECURITY: Locks account after MAX_FAILED_ATTEMPTS wrong PINs.
     * In production: PIN should be hashed, use constant-time comparison.
     */
    public boolean validatePin(String inputPin) {
        if (isLocked) {
            return false;
        }

        if (pin.equals(inputPin)) {
            failedAttempts = 0;
            return true;
        } else {
            failedAttempts++;
            if (failedAttempts >= MAX_FAILED_ATTEMPTS) {
                isLocked = true;
                System.out.println("Account locked due to too many failed attempts!");
            }
            return false;
        }
    }

    /**
     * Withdraw money from account.
     * 
     * @param amount Amount to withdraw
     * @return true if successful, false if insufficient funds
     */
    public boolean withdraw(double amount) {
        if (amount <= 0) {
            System.out.println("Invalid amount");
            return false;
        }
        if (amount > balance) {
            System.out.println("Insufficient balance");
            return false;
        }
        balance -= amount;
        return true;
    }

    /**
     * Deposit money to account.
     */
    public boolean deposit(double amount) {
        if (amount <= 0) {
            System.out.println("Invalid amount");
            return false;
        }
        balance += amount;
        return true;
    }

    public void changePin(String oldPin, String newPin) {
        if (validatePin(oldPin)) {
            this.pin = newPin;
            System.out.println("PIN changed successfully");
        } else {
            System.out.println("Invalid current PIN");
        }
    }

    @Override
    public String toString() {
        return String.format("Account[%s, %s, Balance: $%.2f]",
                accountNumber, accountType, balance);
    }
}
