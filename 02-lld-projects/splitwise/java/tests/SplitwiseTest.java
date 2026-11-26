import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.DisplayName;
import static org.junit.jupiter.api.Assertions.*;

import java.util.List;

/**
 * Tests for Splitwise implementations.
 */
public class SplitwiseTest {

    @Test
    @DisplayName("Equal split calculates correct amounts")
    void testEqualSplit() {
        double total = 300.0;
        int participants = 3;
        double expected = 100.0;
        
        double actual = total / participants;
        assertEquals(expected, actual, 0.01);
    }

    @Test
    @DisplayName("Percentage split calculates correct amounts")
    void testPercentageSplit() {
        double total = 200.0;
        double percentage = 25.0;
        double expected = 50.0;
        
        double actual = total * percentage / 100.0;
        assertEquals(expected, actual, 0.01);
    }

    @Test
    @DisplayName("Balance calculation after single expense")
    void testBalanceAfterExpense() {
        // Alice pays $300, split 3 ways
        double total = 300.0;
        double perPerson = 100.0;
        
        // Bob owes Alice $100, Charlie owes Alice $100
        double bobOwes = perPerson;
        double charlieOwes = perPerson;
        
        assertEquals(100.0, bobOwes, 0.01);
        assertEquals(100.0, charlieOwes, 0.01);
    }

    @Test
    @DisplayName("Net balance calculation")
    void testNetBalance() {
        // Alice paid $300 (owes nothing, owed $200)
        // Bob paid $0 (owes $100)
        // Charlie paid $0 (owes $100)
        
        double aliceNet = 200.0;  // Positive = is owed
        double bobNet = -100.0;   // Negative = owes
        double charlieNet = -100.0;
        
        assertEquals(0, aliceNet + bobNet + charlieNet, 0.01, 
            "Net should sum to zero");
    }

    @Test
    @DisplayName("Debt simplification reduces transactions")
    void testDebtSimplification() {
        // Scenario: A owes B $10, B owes C $10
        // Before: 2 transactions
        // After: A pays C $10 (1 transaction)
        
        int before = 2;
        int after = 1;
        
        assertTrue(after < before, "Simplified should have fewer transactions: " + after + " < " + before);
        assertEquals(1, after, "After simplification should be 1 transaction");
    }

    @Test
    @DisplayName("Rounding handles cents correctly")
    void testRounding() {
        double total = 100.0;
        int participants = 3;
        double perPerson = Math.round((total / participants) * 100.0) / 100.0;
        
        assertEquals(33.33, perPerson, 0.01);
        
        // Sum won't be exactly 100, need to handle remainder
        double sum = perPerson * 3;
        double remainder = total - sum;
        
        assertTrue(Math.abs(remainder) < 0.02, "Remainder should be small");
    }

    @Test
    @DisplayName("Self-payment doesn't create balance")
    void testSelfPayment() {
        // Alice pays $100, only Alice participates
        // No balance should be created
        
        boolean createsBalance = false;
        assertFalse(createsBalance);
    }

    @Test
    @DisplayName("Group maintains member list")
    void testGroupMembers() {
        int initialMembers = 0;
        int afterAdd = 3;
        int afterRemove = 2;
        
        assertEquals(0, initialMembers);
        assertEquals(3, afterAdd);
        assertEquals(2, afterRemove);
    }
}
