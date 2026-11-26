import java.util.UUID;
public class UUIDGen {
    public UUID nextId() {
        return UUID.randomUUID();
    }
    public static void main(String[] args) {
        UUIDGen u = new UUIDGen();
        // Test 1
        assert u.nextId() != null;
        // Test 2
        assert u.nextId() != null;
        // Test 3
        assert u.nextId() != null;
        // Test 4
        assert u.nextId() != null;
        // Test 5
        assert u.nextId() != null;
        // Test 6
        assert u.nextId() != null;
    }
}
