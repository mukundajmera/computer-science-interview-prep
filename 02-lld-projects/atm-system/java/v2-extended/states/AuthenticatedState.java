package states;

import enums.ATMStateType;
import enums.TransactionType;
import models.Card;
import models.Account;
import models.Transaction;

/**
 * AuthenticatedState.java - PIN validated, ready for transactions.
 */
public class AuthenticatedState implements ATMState {

    @Override
    public void insertCard(ATM atm, Card card) {
        System.out.println("Card already inserted");
    }

    @Override
    public boolean authenticatePin(ATM atm, String pin) {
        System.out.println("Already authenticated");
        return true;
    }

    @Override
    public void selectAccount(ATM atm, int accountIndex) {
        var accounts = atm.getCurrentCard().getLinkedAccounts();
        if (accountIndex >= 0 && accountIndex < accounts.size()) {
            atm.setCurrentAccount(accounts.get(accountIndex));
            System.out.println("Selected: " + atm.getCurrentAccount());
        } else {
            System.out.println("Invalid account selection");
        }
    }

    @Override
    public void checkBalance(ATM atm) {
        Account account = atm.getCurrentAccount();
        Transaction tx = new Transaction(TransactionType.BALANCE_INQUIRY, 0, account);
        tx.execute();
        atm.addTransaction(tx);
    }

    @Override
    public boolean withdraw(ATM atm, double amount) {
        Account account = atm.getCurrentAccount();
        Transaction tx = new Transaction(TransactionType.WITHDRAWAL, amount, account);
        boolean success = tx.execute();
        atm.addTransaction(tx);
        return success;
    }

    @Override
    public boolean deposit(ATM atm, double amount) {
        Account account = atm.getCurrentAccount();
        Transaction tx = new Transaction(TransactionType.DEPOSIT, amount, account);
        boolean success = tx.execute();
        atm.addTransaction(tx);
        return success;
    }

    @Override
    public void ejectCard(ATM atm) {
        System.out.println("Card ejected: " + atm.getCurrentCard().getMaskedNumber());
        atm.setCurrentCard(null);
        atm.setCurrentAccount(null);
        atm.setState(new IdleState());
    }

    @Override
    public ATMStateType getStateType() {
        return ATMStateType.AUTHENTICATED;
    }
}
