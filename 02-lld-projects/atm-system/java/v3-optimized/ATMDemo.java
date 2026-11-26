import models.Account;
import models.Transaction;
import enums.AccountType;
import models.Card;
import java.util.*;
import java.util.concurrent.*;
import java.util.concurrent.atomic.*;
import java.util.concurrent.locks.*;

public class ATMDemo {
    public static void main(String[] args) {
        System.out.println("=== ATM System v3 - Optimized Demo ===\n");
        
        // Create accounts
        Account checking = new Account("CHK001", AccountType.CHECKING, 2500.0, "1234");
        Account savings = new Account("SAV001", AccountType.SAVINGS, 10000.0, "1234");
        
        // Create card with multiple accounts
        Card card = new Card("1234567890123456", "John Doe");
        card.linkAccount(checking);
        card.linkAccount(savings);
        
        // Create ATM
        ATM atm = new ATM("ATM001", "Main Street Branch");
        
        try {
            // Demo: Full transaction flow
            System.out.println("--- Complete Transaction Demo ---\n");
            
            // Show ATM cash inventory
            System.out.println("ATM Cash Inventory:");
            for (Map.Entry<Denomination, Integer> entry : atm.getCashInventory().entrySet()) {
                System.out.printf("  $%d bills: %d%n", entry.getKey().getValue(), entry.getValue());
            }
            System.out.printf("Total: $%d%n%n", atm.getTotalCash());
            
            atm.insertCard(card);
            atm.authenticatePin("1234");
            
            // Check balance
            atm.checkBalance();
            
            // Withdraw
            System.out.println("\n[Withdrawing $270]");
            atm.withdraw(270);
            
            // Deposit
            System.out.println("\n[Depositing $150]");
            atm.deposit(150);
            
            // Switch to savings
            System.out.println("\n[Switching to Savings Account]");
            atm.selectAccount(savings);
            atm.checkBalance();
            
            // Transfer
            System.out.println("\n[Transferring $500 to Checking]");
            atm.transfer(checking, 500);
            
            // Show history
            atm.showTransactionHistory();
            
            // Eject card
            System.out.println();
            atm.ejectCard();
            
            // Demo: Concurrent operations
            System.out.println("\n--- Concurrent Transaction Demo ---");
            demoConcurrentTransactions(atm);
            
        } catch (ATMException e) {
            System.err.println("ATM Error: " + e.getMessage());
        } finally {
            atm.shutdown();
        }
        
        System.out.println("\n=== Demo Complete ===");
    }
    
    private static void demoConcurrentTransactions(ATM atm) {
        Account acc1 = new Account("ACC001", AccountType.CHECKING, 1000.0, "1111");
        Account acc2 = new Account("ACC002", AccountType.CHECKING, 1000.0, "2222");
        
        ExecutorService executor = Executors.newFixedThreadPool(4);
        CountDownLatch latch = new CountDownLatch(4);
        
        // Simulate concurrent transfers
        for (int i = 0; i < 2; i++) {
            final int amount = 100 * (i + 1);
            executor.submit(() -> {
                try {
                    TransferTransaction t = new TransferTransaction(acc1, acc2, amount);
                    t.execute();
                    System.out.println("Transfer $" + amount + " from ACC001 to ACC002: SUCCESS");
                } catch (ATMException e) {
                    System.out.println("Transfer failed: " + e.getMessage());
                } finally {
                    latch.countDown();
                }
            });
            
            executor.submit(() -> {
                try {
                    TransferTransaction t = new TransferTransaction(acc2, acc1, amount);
                    t.execute();
                    System.out.println("Transfer $" + amount + " from ACC002 to ACC001: SUCCESS");
                } catch (ATMException e) {
                    System.out.println("Transfer failed: " + e.getMessage());
                } finally {
                    latch.countDown();
                }
            });
        }
        
        try {
            latch.await(10, TimeUnit.SECONDS);
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }
        
        executor.shutdown();
        
        System.out.printf("Final balance ACC001: $%.2f%n", acc1.getBalance());
        System.out.printf("Final balance ACC002: $%.2f%n", acc2.getBalance());
    }
}
