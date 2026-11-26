
import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

public class OptimizedTest {
    @Test
    public void testSurgePricing() {
        PricingStrategy strategy = new SurgePricingStrategy();
        assertEquals(12.0, strategy.calculatePrice(10.0, 3, 2), 0.01);
        assertEquals(15.0, strategy.calculatePrice(10.0, 5, 2), 0.01);
        assertEquals(20.0, strategy.calculatePrice(10.0, 5, 0), 0.01);
    }
    
    @Test
    public void testOrderStateTransition() {
        Order order = new Order("O1", 10.0);
        
        order.transitionState(OrderState.CREATED, OrderState.ACCEPTED);
        assertEquals(OrderState.ACCEPTED, order.getState());
        
        assertThrows(IllegalStateException.class, () -> {
            order.transitionState(OrderState.ACCEPTED, OrderState.DELIVERED);
        });
    }
}
