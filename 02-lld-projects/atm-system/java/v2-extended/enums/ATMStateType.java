package enums;

/**
 * ATMStateType.java - ATM machine states for State Pattern.
 * 
 * State transitions:
 * IDLE → HAS_CARD → AUTHENTICATED → TRANSACTION → AUTHENTICATED/IDLE
 */
public enum ATMStateType {
    IDLE, // Waiting for card
    HAS_CARD, // Card inserted, awaiting PIN
    AUTHENTICATED, // PIN validated, ready for transactions
    TRANSACTION // Processing a transaction
}
