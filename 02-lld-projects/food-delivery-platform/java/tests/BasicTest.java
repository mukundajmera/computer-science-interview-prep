
import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

public class BasicTest {
    @Test
    public void testMenuAndCart() {
        Menu menu = new Menu();
        MenuItem item = new MenuItem("1", "Burger", 10.0);
        menu.addItem(item);
        
        Cart cart = new Cart();
        cart.addItem(item);
        
        assertEquals(1, cart.getItems().size());
        assertEquals(10.0, cart.getTotal());
    }

    @Test
    public void testOrderState() {
        Order order = new Order("O1", null, 10.0);
        assertEquals(OrderState.CREATED, order.getState());
        order.setState(OrderState.RESERVATION);
        assertEquals(OrderState.RESERVATION, order.getState());
    }
}
