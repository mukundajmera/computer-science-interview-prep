package states;

import enums.ATMStateType;
import models.Card;

/**
 * IdleState.java - ATM waiting for card.
 */
public class IdleState implements ATMState {

    @Override
    public void insertCard(ATM atm, Card card) {
        atm.setCurrentCard(card);
        atm.setState(new HasCardState());
        System.out.println("Card inserted: " + card.getMaskedNumber());
    }

    @Override
    public boolean authenticatePin(ATM atm, String pin) {
        System.out.println("Please insert card first");
        return false;
    }

    @Override
    public void selectAccount(ATM atm, int accountIndex) {
        System.out.println("Please insert card first");
    }

    @Override
    public void checkBalance(ATM atm) {
        System.out.println("Please insert card first");
    }

    @Override
    public boolean withdraw(ATM atm, double amount) {
        System.out.println("Please insert card first");
        return false;
    }

    @Override
    public boolean deposit(ATM atm, double amount) {
        System.out.println("Please insert card first");
        return false;
    }

    @Override
    public void ejectCard(ATM atm) {
        System.out.println("No card to eject");
    }

    @Override
    public ATMStateType getStateType() {
        return ATMStateType.IDLE;
    }
}
