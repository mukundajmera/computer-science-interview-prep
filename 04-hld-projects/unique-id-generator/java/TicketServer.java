public class TicketServer {
    private long val = 0;
    public long nextId() {
        return ++val;
    }
    public static void main(String[] args) {
        TicketServer t = new TicketServer();
        // Test 1
        assert t.nextId() == 1;
        // Test 2
        assert t.nextId() == 2;
        // Test 3
        assert t.nextId() == 3;
        // Test 4
        assert t.nextId() == 4;
        // Test 5
        assert t.nextId() == 5;
        // Test 6
        assert t.nextId() == 6;
    }
}
