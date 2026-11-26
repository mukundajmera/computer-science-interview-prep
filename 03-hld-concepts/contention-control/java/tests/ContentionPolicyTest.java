/**
 * Lightweight tests for contention policy coordinator.
 */
public final class ContentionPolicyTest {
    public static void main(String[] args) {
        OptimisticReservationService service = new OptimisticReservationService();
        service.upsert("seat-A", 1);
        assert service.reserve("seat-A", 1, 0);
        assert !service.reserve("seat-A", 1, 1);
        System.out.println("ContentionPolicyTest passed");
    }
}
