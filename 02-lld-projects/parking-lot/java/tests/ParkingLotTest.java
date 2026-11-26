package v1_basic;

import org.junit.jupiter.api.*;
import static org.junit.jupiter.api.Assertions.*;

/**
 * Unit tests for Parking Lot System
 */
class ParkingLotTest {

    @BeforeEach
    void setUp() {
        ParkingLot.resetInstance();
    }

    @AfterEach
    void tearDown() {
        ParkingLot.resetInstance();
    }

    // ============ Vehicle Tests ============

    @Test
    @DisplayName("Vehicle factory creates correct vehicle types")
    void testVehicleFactory() {
        Vehicle motorcycle = VehicleFactory.createVehicle(VehicleType.MOTORCYCLE, "M-001");
        Vehicle car = VehicleFactory.createVehicle(VehicleType.CAR, "C-001");
        Vehicle truck = VehicleFactory.createVehicle(VehicleType.TRUCK, "T-001");

        assertEquals(VehicleType.MOTORCYCLE, motorcycle.getType());
        assertEquals(VehicleType.CAR, car.getType());
        assertEquals(VehicleType.TRUCK, truck.getType());
    }

    @Test
    @DisplayName("Vehicle stores license plate correctly")
    void testVehicleLicensePlate() {
        Vehicle car = new Car("ABC-123");
        assertEquals("ABC-123", car.getLicensePlate());
    }

    // ============ ParkingSpot Tests ============

    @Test
    @DisplayName("Motorcycle spot only fits motorcycles")
    void testMotorcycleSpotFitsOnlyMotorcycles() {
        ParkingSpot spot = new ParkingSpot("F1-M001", SpotType.MOTORCYCLE_SPOT, 1);
        
        Vehicle motorcycle = new Motorcycle("M-001");
        Vehicle car = new Car("C-001");
        Vehicle truck = new Truck("T-001");

        assertTrue(spot.canFit(motorcycle));
        assertFalse(spot.canFit(car));
        assertFalse(spot.canFit(truck));
    }

    @Test
    @DisplayName("Compact spot fits motorcycles and cars")
    void testCompactSpotFitsMotorcyclesAndCars() {
        ParkingSpot spot = new ParkingSpot("F1-C001", SpotType.COMPACT_SPOT, 1);
        
        Vehicle motorcycle = new Motorcycle("M-001");
        Vehicle car = new Car("C-001");
        Vehicle truck = new Truck("T-001");

        assertTrue(spot.canFit(motorcycle));
        assertTrue(spot.canFit(car));
        assertFalse(spot.canFit(truck));
    }

    @Test
    @DisplayName("Large spot fits all vehicle types")
    void testLargeSpotFitsAllVehicles() {
        ParkingSpot spot = new ParkingSpot("F1-L001", SpotType.LARGE_SPOT, 1);
        
        Vehicle motorcycle = new Motorcycle("M-001");
        Vehicle car = new Car("C-001");
        Vehicle truck = new Truck("T-001");

        assertTrue(spot.canFit(motorcycle));
        assertTrue(spot.canFit(car));
        assertTrue(spot.canFit(truck));
    }

    @Test
    @DisplayName("Parking and unparking works correctly")
    void testParkAndUnpark() {
        ParkingSpot spot = new ParkingSpot("F1-C001", SpotType.COMPACT_SPOT, 1);
        Vehicle car = new Car("C-001");

        assertTrue(spot.isAvailable());
        assertTrue(spot.park(car));
        assertFalse(spot.isAvailable());
        assertTrue(spot.isOccupied());

        Vehicle unparked = spot.unpark();
        assertEquals(car, unparked);
        assertTrue(spot.isAvailable());
    }

    @Test
    @DisplayName("Cannot park in occupied spot")
    void testCannotParkInOccupiedSpot() {
        ParkingSpot spot = new ParkingSpot("F1-C001", SpotType.COMPACT_SPOT, 1);
        Vehicle car1 = new Car("C-001");
        Vehicle car2 = new Car("C-002");

        assertTrue(spot.park(car1));
        assertFalse(spot.park(car2));
    }

    // ============ Floor Tests ============

    @Test
    @DisplayName("Floor initializes with correct spot counts")
    void testFloorInitialization() {
        Floor floor = new Floor(1, 5, 10, 3);
        assertEquals(18, floor.getTotalCapacity());
    }

    @Test
    @DisplayName("Floor finds and assigns available spot")
    void testFloorParkVehicle() {
        Floor floor = new Floor(1, 5, 10, 3);
        Vehicle car = new Car("C-001");

        ParkingSpot spot = floor.parkVehicle(car);
        assertNotNull(spot);
        assertEquals(car, spot.getVehicle());
    }

    @Test
    @DisplayName("Floor returns null when no suitable spot available")
    void testFloorFullForVehicleType() {
        Floor floor = new Floor(1, 0, 0, 1); // Only 1 large spot
        
        Vehicle truck1 = new Truck("T-001");
        Vehicle truck2 = new Truck("T-002");

        assertNotNull(floor.parkVehicle(truck1));
        assertNull(floor.parkVehicle(truck2));
    }

    // ============ ParkingLot Tests ============

    @Test
    @DisplayName("ParkingLot singleton returns same instance")
    void testSingletonInstance() {
        ParkingLot lot1 = ParkingLot.getInstance();
        ParkingLot lot2 = ParkingLot.getInstance();
        
        assertSame(lot1, lot2);
    }

    @Test
    @DisplayName("ParkingLot parks vehicle and returns ticket")
    void testParkVehicle() {
        ParkingLot lot = ParkingLot.getInstance();
        lot.addFloor(5, 10, 3);
        
        Vehicle car = new Car("C-001");
        Ticket ticket = lot.parkVehicle(car);

        assertNotNull(ticket);
        assertEquals(car, ticket.getVehicle());
        assertNotNull(ticket.getSpot());
    }

    @Test
    @DisplayName("ParkingLot prevents double parking")
    void testDoubleParkingPrevention() {
        ParkingLot lot = ParkingLot.getInstance();
        lot.addFloor(5, 10, 3);
        
        Vehicle car = new Car("C-001");
        Ticket ticket1 = lot.parkVehicle(car);
        Ticket ticket2 = lot.parkVehicle(car);

        assertNotNull(ticket1);
        assertNull(ticket2); // Should fail - already parked
    }

    @Test
    @DisplayName("ParkingLot unparks vehicle and calculates fee")
    void testUnparkVehicle() {
        ParkingLot lot = ParkingLot.getInstance();
        lot.addFloor(5, 10, 3);
        
        Vehicle car = new Car("C-001");
        Ticket ticket = lot.parkVehicle(car);
        
        double fee = lot.unparkVehicle(ticket);
        
        assertTrue(fee >= 0);
        assertNull(lot.findVehicle("C-001")); // Vehicle should be removed
    }

    @Test
    @DisplayName("ParkingLot finds vehicle by license plate")
    void testFindVehicle() {
        ParkingLot lot = ParkingLot.getInstance();
        lot.addFloor(5, 10, 3);
        
        Vehicle car = new Car("C-001");
        lot.parkVehicle(car);

        ParkingSpot spot = lot.findVehicle("C-001");
        assertNotNull(spot);
        assertEquals(car, spot.getVehicle());
    }

    @Test
    @DisplayName("ParkingLot returns correct available spot count")
    void testAvailableSpotCount() {
        ParkingLot lot = ParkingLot.getInstance();
        lot.addFloor(5, 10, 3); // 5 motorcycle, 10 compact, 3 large

        // Cars can use compact + large = 13
        assertEquals(13, lot.getAvailableSpots(VehicleType.CAR));
        
        Vehicle car = new Car("C-001");
        lot.parkVehicle(car);
        
        assertEquals(12, lot.getAvailableSpots(VehicleType.CAR));
    }

    @Test
    @DisplayName("ParkingLot throws exception for null vehicle")
    void testNullVehicleThrowsException() {
        ParkingLot lot = ParkingLot.getInstance();
        lot.addFloor(5, 10, 3);

        assertThrows(IllegalArgumentException.class, () -> lot.parkVehicle(null));
    }

    // ============ Ticket Tests ============

    @Test
    @DisplayName("Ticket generates unique ID")
    void testTicketUniqueId() {
        ParkingLot lot = ParkingLot.getInstance();
        lot.addFloor(5, 10, 3);
        
        Vehicle car1 = new Car("C-001");
        Vehicle car2 = new Car("C-002");
        
        Ticket ticket1 = lot.parkVehicle(car1);
        Ticket ticket2 = lot.parkVehicle(car2);

        assertNotEquals(ticket1.getTicketId(), ticket2.getTicketId());
    }

    @Test
    @DisplayName("Ticket duration is at least 1 hour")
    void testTicketMinimumDuration() {
        ParkingLot lot = ParkingLot.getInstance();
        lot.addFloor(5, 10, 3);
        
        Vehicle car = new Car("C-001");
        Ticket ticket = lot.parkVehicle(car);

        assertTrue(ticket.getDurationHours() >= 1);
    }

    // ============ Pricing Tests ============

    @Test
    @DisplayName("Hourly pricing calculates correctly by vehicle type")
    void testHourlyPricing() {
        PricingStrategy pricing = new HourlyPricing();
        
        ParkingLot lot = ParkingLot.getInstance();
        lot.addFloor(5, 10, 3);
        
        Vehicle motorcycle = new Motorcycle("M-001");
        Vehicle car = new Car("C-001");
        Vehicle truck = new Truck("T-001");
        
        Ticket motoTicket = lot.parkVehicle(motorcycle);
        Ticket carTicket = lot.parkVehicle(car);
        Ticket truckTicket = lot.parkVehicle(truck);
        
        // For 1 hour parking
        assertEquals(1.0, pricing.calculateFee(motoTicket)); // $1/hour
        assertEquals(2.0, pricing.calculateFee(carTicket));  // $2/hour
        assertEquals(4.0, pricing.calculateFee(truckTicket)); // $4/hour
    }

    // ============ V3 Concurrent Tests ============

    @Test
    @DisplayName("Multiple threads should be able to park concurrently")
    void testConcurrentParking() throws InterruptedException {
        ParkingLot lot = ParkingLot.getInstance("Concurrent Lot");
        lot.addFloor(10, 30, 10);
        
        int numThreads = 8;
        int vehiclesPerThread = 5;
        java.util.concurrent.CountDownLatch latch = new java.util.concurrent.CountDownLatch(numThreads);
        java.util.List<Ticket> tickets = java.util.Collections.synchronizedList(new java.util.ArrayList<>());
        
        for (int i = 0; i < numThreads; i++) {
            final int threadId = i;
            new Thread(() -> {
                for (int j = 0; j < vehiclesPerThread; j++) {
                    Vehicle car = new Car("T" + threadId + "-V" + String.format("%03d", j));
                    Ticket ticket = lot.parkVehicle(car);
                    if (ticket != null) {
                        tickets.add(ticket);
                    }
                }
                latch.countDown();
            }).start();
        }
        
        latch.await();
        
        assertEquals(numThreads * vehiclesPerThread, tickets.size());
        assertEquals(numThreads * vehiclesPerThread, lot.getActiveVehicleCount());
    }

    @Test
    @DisplayName("No double parking even with concurrent attempts")
    void testNoDoubleParkingConcurrent() throws InterruptedException {
        ParkingLot lot = ParkingLot.getInstance("Concurrent Lot");
        lot.addFloor(10, 30, 10);
        
        int numThreads = 10;
        java.util.concurrent.CountDownLatch latch = new java.util.concurrent.CountDownLatch(numThreads);
        java.util.concurrent.atomic.AtomicInteger successful = new java.util.concurrent.atomic.AtomicInteger(0);
        
        for (int i = 0; i < numThreads; i++) {
            new Thread(() -> {
                Vehicle car = new Car("SAME-001");
                Ticket ticket = lot.parkVehicle(car);
                if (ticket != null) {
                    successful.incrementAndGet();
                }
                latch.countDown();
            }).start();
        }
        
        latch.await();
        
        assertEquals(1, successful.get());
        assertEquals(1, lot.getActiveVehicleCount());
    }

    // ============ Integration Tests ============

    @Test
    @DisplayName("Full parking lot workflow")
    void testFullWorkflow() {
        ParkingLot lot = ParkingLot.getInstance("Test Lot");
        lot.addFloor(2, 3, 1);
        
        // Park vehicles
        Vehicle moto = new Motorcycle("M-001");
        Vehicle car1 = new Car("C-001");
        Vehicle car2 = new Car("C-002");
        Vehicle truck = new Truck("T-001");
        
        Ticket motoTicket = lot.parkVehicle(moto);
        Ticket car1Ticket = lot.parkVehicle(car1);
        Ticket car2Ticket = lot.parkVehicle(car2);
        Ticket truckTicket = lot.parkVehicle(truck);
        
        assertNotNull(motoTicket);
        assertNotNull(car1Ticket);
        assertNotNull(car2Ticket);
        assertNotNull(truckTicket);
        
        assertEquals(4, lot.getActiveVehicleCount());
        
        // Unpark one car
        double fee = lot.unparkVehicle(car1Ticket);
        assertTrue(fee >= 0);
        assertEquals(3, lot.getActiveVehicleCount());
        
        // Park another car in freed spot
        Vehicle car3 = new Car("C-003");
        Ticket car3Ticket = lot.parkVehicle(car3);
        assertNotNull(car3Ticket);
        
        // Cannot park same car twice
        Ticket duplicate = lot.parkVehicle(car2);
        assertNull(duplicate);
    }
}
