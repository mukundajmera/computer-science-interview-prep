package states;

import models.Card;

/**
 * ATMState.java - State interface for ATM State Pattern.
 * 
 * DESIGN PATTERN: State Pattern
 * - Each state handles operations differently
 * - ATM delegates to current state
 * - Clean state transitions
 */
public interface ATMState {
    void insertCard(ATM atm, Card card);

    boolean authenticatePin(ATM atm, String pin);

    void selectAccount(ATM atm, int accountIndex);

    void checkBalance(ATM atm);

    boolean withdraw(ATM atm, double amount);

    boolean deposit(ATM atm, double amount);

    void ejectCard(ATM atm);

    ATMStateType getStateType();
}
