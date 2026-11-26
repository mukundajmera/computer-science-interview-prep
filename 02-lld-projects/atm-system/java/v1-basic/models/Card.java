package models;

/**
 * Card.java - ATM/Debit card linked to an account.
 * 
 * DESIGN: Card is separate from Account for flexibility
 * - One account can have multiple cards
 * - Card can be blocked independently
 */
public class Card {
    private final String cardNumber;
    private final String holderName;
    private final Account linkedAccount;

    public Card(String cardNumber, String holderName, Account linkedAccount) {
        this.cardNumber = cardNumber;
        this.holderName = holderName;
        this.linkedAccount = linkedAccount;
    }

    public String getCardNumber() {
        return cardNumber;
    }

    public String getHolderName() {
        return holderName;
    }

    public Account getLinkedAccount() {
        return linkedAccount;
    }

    /**
     * Return masked card number for display.
     * SECURITY: Never show full card number.
     */
    public String getMaskedNumber() {
        return "XXXX-XXXX-XXXX-" + cardNumber.substring(cardNumber.length() - 4);
    }
}
