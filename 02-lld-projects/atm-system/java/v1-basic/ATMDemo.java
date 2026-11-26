import models.Account;
import models.Transaction;
import enums.AccountType;
import models.Card;
import java.util.*;

public class ATMDemo {
    public static void main(String[] args) {
        System.out.println("=== ATM System v1 - Basic Demo ===\n");
        
        // Create account and card
        Account account = new Account("ACC001", AccountType.CHECKING, 1000.0, "1234");
        Card card = new Card("1234567890123456", "John Doe", account);
        
        // Create ATM
        ATM atm = new ATM("ATM001", "Main Street Branch");
        
        // Demo: Normal flow
        System.out.println("--- Normal Transaction Flow ---");
        atm.insertCard(card);
        atm.authenticatePin("1234");
        atm.checkBalance();
        atm.withdraw(200);
        atm.checkBalance();
        atm.deposit(50);
        atm.checkBalance();
        atm.ejectCard();
        
        // Demo: Failed authentication
        System.out.println("\n--- Failed Authentication Demo ---");
        Account account2 = new Account("ACC002", AccountType.SAVINGS, 500.0, "5678");
        Card card2 = new Card("9876543210987654", "Jane Smith", account2);
        
        atm.insertCard(card2);
        atm.authenticatePin("0000");  // Wrong PIN
        atm.authenticatePin("1111");  // Wrong PIN
        atm.authenticatePin("2222");  // Wrong PIN - should lock
        atm.ejectCard();
        
        // Print transaction log
        atm.printTransactionLog();
        
        System.out.println("\n=== Demo Complete ===");
    }
}
