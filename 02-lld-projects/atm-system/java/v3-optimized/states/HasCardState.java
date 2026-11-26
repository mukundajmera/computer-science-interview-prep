package states;

import enums.ATMStateType;
import models.Card;
import models.Account;

/**
 * HasCardState.java - Card inserted, awaiting PIN.
 */
public class HasCardState implements ATMState {

    @Override
    public void insertCard(ATM atm, Card card) {
        System.out.println("Card already inserted");
    }

    @Override
    public boolean authenticatePin(ATM atm, String pin) {
        Account account = atm.getCurrentAccount();
        if (account == null) {
            account = atm.getCurrentCard().getPrimaryAccount();
            atm.setCurrentAccount(account);
        }

        if (account.isLocked()) {
            System.out.println("Account is locked. Please contact bank.");
            atm.ejectCard();
            return false;
        }

        if (account.validatePin(pin)) {
            atm.setState(new AuthenticatedState());
            System.out.println("Authentication successful!");
            return true;
        } else {
            System.out.println("Invalid PIN");
            if (account.isLocked()) {
                atm.ejectCard();
            }
            return false;
        }
    }

    @Override
    public void selectAccount(ATM atm, int accountIndex) {
        System.out.println("Please authenticate first");
    }

    @Override
    public void checkBalance(ATM atm) {
        System.out.println("Please authenticate first");
    }

    @Override
    public boolean withdraw(ATM atm, double amount) {
        System.out.println("Please authenticate first");
        return false;
    }

    @Override
    public boolean deposit(ATM atm, double amount) {
        System.out.println("Please authenticate first");
        return false;
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
        return ATMStateType.HAS_CARD;
    }
}
