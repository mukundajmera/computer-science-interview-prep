/**
 * Strategy Pattern - Unit Tests
 */

import org.junit.jupiter.api.*;
import static org.junit.jupiter.api.Assertions.*;

class StrategyTest {
    
    // Test basic strategy switching
    @Test
    void testStrategySwitching() {
        // Simple calculation context
        class Calculator {
            private java.util.function.BiFunction<Integer, Integer, Integer> strategy;
            
            void setStrategy(java.util.function.BiFunction<Integer, Integer, Integer> s) {
                this.strategy = s;
            }
            
            int execute(int a, int b) {
                return strategy.apply(a, b);
            }
        }
        
        Calculator calc = new Calculator();
        
        calc.setStrategy((a, b) -> a + b);
        assertEquals(8, calc.execute(5, 3));
        
        calc.setStrategy((a, b) -> a - b);
        assertEquals(2, calc.execute(5, 3));
        
        calc.setStrategy((a, b) -> a * b);
        assertEquals(15, calc.execute(5, 3));
    }
    
    // Test discount strategies
    @Test
    void testDiscountStrategies() {
        // Percentage discount
        double price = 100.0;
        double tenPercentOff = price * 0.9;
        assertEquals(90.0, tenPercentOff, 0.01);
        
        // Fixed discount
        double fifteenOff = Math.max(0, price - 15);
        assertEquals(85.0, fifteenOff, 0.01);
    }
    
    // Test null strategy handling
    @Test
    void testNullStrategyProtection() {
        class Context {
            private Runnable strategy;
            
            void setStrategy(Runnable s) {
                this.strategy = s;
            }
            
            void execute() {
                if (strategy == null) {
                    throw new IllegalStateException("Strategy not set");
                }
                strategy.run();
            }
        }
        
        Context ctx = new Context();
        assertThrows(IllegalStateException.class, ctx::execute);
        
        ctx.setStrategy(() -> {});
        assertDoesNotThrow(ctx::execute);
    }
    
    // Test strategy independence
    @Test
    void testStrategyIndependence() {
        int[] data = {3, 1, 4, 1, 5, 9, 2, 6};
        int[] sorted = java.util.Arrays.stream(data).sorted().toArray();
        
        // Different sort "strategies" should produce same result
        int[] copy1 = data.clone();
        int[] copy2 = data.clone();
        java.util.Arrays.sort(copy1);
        java.util.Arrays.sort(copy2);
        
        assertArrayEquals(sorted, copy1);
        assertArrayEquals(sorted, copy2);
    }
}
