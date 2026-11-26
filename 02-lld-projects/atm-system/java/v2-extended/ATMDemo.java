import models.Account;
import models.Transaction;
import enums.AccountType;
import models.Card;
import java.util.*;

public class ATMDemo {
    public static void main(String[] args) {
        System.out.println("=== ATM System v2 - Extended Demo ===\n");
        
        // Create accounts
        Account checking = new Account("CHK001", AccountType.CHECKING, 2500.0, "1234");
        Account savings = new Account("SAV001", AccountType.SAVINGS, 10000.0, "1234");
        
        // Create card with multiple accounts
        Card card = new Card("1234567890123456", "John Doe");
        card.linkAccount(checking);
        card.linkAccount(savings);
        
        // Create ATM
        ATM atm = new ATM("ATM001", "Main Street Branch");
        
        // Demo: Full transaction flow
        System.out.println("--- Complete Transaction Demo ---\n");
        
        atm.insertCard(card);
        atm.enterPin("1234");
        
        // Check balance
        System.out.println("\n[Checking Balance]");
        atm.checkBalance();
        
        // Withdraw
        System.out.println("\n[Withdrawing $200]");
        atm.withdraw(200);
        
        // Deposit
        System.out.println("\n[Depositing $50]");
        atm.deposit(50);
        
        // Switch to savings and transfer
        System.out.println("\n[Switching to Savings Account]");
        atm.selectAccount(savings);
        atm.checkBalance();
        
        // Transfer from savings to checking
        System.out.println("\n[Transferring $500 to Checking]");
        atm.transfer(checking, 500);
        
        // Show transaction history
        System.out.println("\n[Transaction History - Savings]");
        atm.showTransactionHistory();
        
        // Switch back and check
        System.out.println("\n[Switching to Checking]");
        atm.selectAccount(checking);
        atm.checkBalance();
        atm.showTransactionHistory();
        
        atm.ejectCard();
        
        System.out.println("\n=== Demo Complete ===");
    }
}
