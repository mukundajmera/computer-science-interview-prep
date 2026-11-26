import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

public class PaymentSystemV1Test {
    @Test
    void v1PaymentComponentsExposeStableDescriptions() {
        PaymentService service = new PaymentService();
        PaymentRequest request = new PaymentRequest();
        Money money = new Money();
        PaymentMethod method = new PaymentMethod();
        PaymentGateway gateway = new PaymentGateway();
        TransactionStore store = new TransactionStore();

        assertEquals("PaymentService", service.getId());
        assertEquals("PaymentService:PaymentService", service.describe());
        assertEquals("PaymentRequest:PaymentRequest", request.describe());
        assertEquals("Money:Money", money.describe());
        assertEquals("PaymentMethod:PaymentMethod", method.describe());
        assertEquals("PaymentGateway:PaymentGateway", gateway.describe());
        assertEquals("TransactionStore:TransactionStore", store.describe());
    }

    @Test
    void v1PaymentStatusFlowIncludesTerminalStates() {
        assertArrayEquals(
            new PaymentStatus[] {
                PaymentStatus.CREATED,
                PaymentStatus.RUNNING,
                PaymentStatus.SUCCEEDED,
                PaymentStatus.FAILED
            },
            PaymentStatus.values()
        );
    }
}
