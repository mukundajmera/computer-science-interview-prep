public class Demo {
    public static void main(String[] args) {
        IdempotencyStore store = new IdempotencyStore();
        System.out.println(store.processCreateRequest("k1", "order-1"));
        System.out.println(store.processCreateRequest("k1", "order-2"));
    }
}
