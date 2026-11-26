import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.BeforeEach;
import static org.junit.jupiter.api.Assertions.*;

public class HotelManagementSystemAll_versionsTest {
    
    private HotelManager manager;

    @BeforeEach
    public void setup() {
        manager = new HotelManager();
    }

    @Test
    public void testHousekeepingStatus() {
        Room room = new Room("101", RoomType.STANDARD);
        assertEquals(HousekeepingStatus.CLEAN, room.getStatus());
        
        manager.addRoom(room);
        manager.updateHousekeepingStatus("101", HousekeepingStatus.INSPECTED);
        
        assertEquals(HousekeepingStatus.INSPECTED, room.getStatus());
    }

    @Test
    public void testCheckIn() {
        Room room = new Room("102", RoomType.DELUXE);
        manager.addRoom(room);
        manager.updateHousekeepingStatus("102", HousekeepingStatus.INSPECTED);
        
        Stay stay = manager.checkIn("RES-1", "Alice", RoomType.DELUXE);
        
        assertNotNull(stay);
        assertEquals("Alice", stay.getGuestName());
        assertEquals("102", stay.getRoom().getRoomId());
        assertTrue(stay.getRoom().isOccupied());
    }

    @Test
    public void testFolioBilling() {
        Room room = new Room("103", RoomType.SUITE);
        manager.addRoom(room);
        manager.updateHousekeepingStatus("103", HousekeepingStatus.INSPECTED);
        
        Stay stay = manager.checkIn("RES-2", "Bob", RoomType.SUITE);
        
        manager.postCharge("103", "Room Service", 50.0);
        manager.postCharge("103", "Spa", 100.0);
        
        double expectedBalanceBefore = 150.0;
        assertEquals(expectedBalanceBefore, stay.getFolio().getBalance());
        
        manager.settleFolio("103", 100.0);
        double expectedBalanceAfter = 50.0;
        assertEquals(expectedBalanceAfter, stay.getFolio().getBalance());
    }

    @Test
    public void testRoomKeys() {
        Room room = new Room("104", RoomType.STANDARD);
        manager.addRoom(room);
        manager.updateHousekeepingStatus("104", HousekeepingStatus.INSPECTED);
        
        Stay stay = manager.checkIn("RES-3", "Charlie", RoomType.STANDARD);
        
        RoomKey key1 = stay.issueKey();
        RoomKey key2 = stay.issueKey();
        
        assertTrue(key1.isActive());
        assertTrue(key2.isActive());
        assertEquals(2, stay.getKeys().size());
        
        manager.postCharge("104", "Minibar", 10.0);
        manager.settleFolio("104", 10.0);
        manager.checkOut("104");
        
        assertFalse(key1.isActive());
        assertFalse(key2.isActive());
    }

    @Test
    public void testCheckOutUnsettledFolio() {
        Room room = new Room("105", RoomType.DELUXE);
        manager.addRoom(room);
        manager.updateHousekeepingStatus("105", HousekeepingStatus.INSPECTED);
        
        Stay stay = manager.checkIn("RES-4", "Dave", RoomType.DELUXE);
        
        manager.postCharge("105", "Laundry", 20.0);
        
        Exception exception = assertThrows(IllegalStateException.class, () -> {
            manager.checkOut("105");
        });
        
        assertEquals("Folio must be settled before check-out", exception.getMessage());
        assertTrue(stay.getRoom().isOccupied());
    }
}
