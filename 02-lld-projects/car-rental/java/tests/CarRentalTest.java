import org.junit.jupiter.api.*;
import static org.junit.jupiter.api.Assertions.*;
import java.time.LocalDate;
import java.util.concurrent.*;

/**
 * Car Rental System Test Suite
 */
public class CarRentalTest {

    private RentalService service;
    private Vehicle car;
    private Vehicle suv;
    private Customer customer;

    @BeforeEach
    void setUp() {
        RentalService.resetInstance();
        service = RentalService.getInstance();
        
        car = new Vehicle("V1", "ABC-123", "Toyota", "Camry", VehicleType.CAR, 50.0);
        suv = new Vehicle("V2", "DEF-456", "Honda", "CR-V", VehicleType.SUV, 60.0);
        
        service.addVehicle(car);
        service.addVehicle(suv);
        
        customer = service.registerCustomer("C1", "John", "john@test.com", "555-1234", "DL123");
    }

    @Test
    @DisplayName("Vehicle creation works correctly")
    void testVehicleCreation() {
        assertNotNull(car);
        assertEquals("Toyota", car.getMake());
        assertEquals(VehicleStatus.AVAILABLE, car.getStatus());
    }

    @Test
    @DisplayName("Customer registration works")
    void testCustomerRegistration() {
        assertNotNull(customer);
        assertEquals("John", customer.getName());
        assertEquals(0, customer.getLoyaltyPoints());
    }

    @Test
    @DisplayName("Search available vehicles by type")
    void testSearchAvailable() {
        LocalDate start = LocalDate.now();
        LocalDate end = start.plusDays(3);
        
        var suvs = service.searchAvailable(VehicleType.SUV, start, end);
        
        assertEquals(1, suvs.size());
        assertEquals("Honda", suvs.get(0).getMake());
    }

    @Test
    @DisplayName("Make reservation successfully")
    void testMakeReservation() {
        LocalDate start = LocalDate.now();
        LocalDate end = start.plusDays(3);
        
        Reservation reservation = service.makeReservation(customer, car, start, end, InsuranceType.BASIC);
        
        assertNotNull(reservation);
        assertEquals(ReservationStatus.CONFIRMED, reservation.getStatus());
        assertTrue(reservation.getTotalCost() > 0);
    }

    @Test
    @DisplayName("Cannot double-book same vehicle for overlapping dates")
    void testPreventDoubleBooking() {
        LocalDate start = LocalDate.now();
        LocalDate end = start.plusDays(3);
        
        service.makeReservation(customer, car, start, end, InsuranceType.NONE);
        
        Customer customer2 = service.registerCustomer("C2", "Jane", "jane@test.com", "555-5678", "DL456");
        
        assertThrows(IllegalStateException.class, () -> {
            service.makeReservation(customer2, car, start.plusDays(1), end.plusDays(1), InsuranceType.NONE);
        });
    }

    @Test
    @DisplayName("Vehicle becomes available after return")
    void testReturnVehicle() {
        LocalDate start = LocalDate.now();
        LocalDate end = start.plusDays(3);
        
        Reservation reservation = service.makeReservation(customer, car, start, end, InsuranceType.NONE);
        service.pickupVehicle(reservation);
        service.returnVehicle(reservation, 100, null, end);
        
        assertEquals(ReservationStatus.COMPLETED, reservation.getStatus());
        assertTrue(car.isAvailable());
    }

    @Test
    @DisplayName("Late return incurs penalty")
    void testLateReturnPenalty() {
        LocalDate start = LocalDate.now();
        LocalDate end = start.plusDays(3);
        LocalDate lateReturn = end.plusDays(2);
        
        Reservation reservation = service.makeReservation(customer, car, start, end, InsuranceType.NONE);
        double originalCost = reservation.getTotalCost();
        
        service.pickupVehicle(reservation);
        service.returnVehicle(reservation, 100, null, lateReturn);
        
        assertTrue(reservation.getLateFeeCost() > 0);
        assertTrue(reservation.getTotalCost() > originalCost);
    }

    @Test
    @DisplayName("Damage report increases cost")
    void testDamageReport() {
        LocalDate start = LocalDate.now();
        LocalDate end = start.plusDays(3);
        
        Reservation reservation = service.makeReservation(customer, car, start, end, InsuranceType.NONE);
        double originalCost = reservation.getTotalCost();
        
        service.pickupVehicle(reservation);
        DamageReport damage = service.reportDamage(car, "Scratch", DamageSeverity.MINOR);
        service.returnVehicle(reservation, 100, damage, end);
        
        assertTrue(reservation.getDamageCost() > 0);
        assertTrue(reservation.getTotalCost() > originalCost);
    }

    @Test
    @DisplayName("Premium insurance covers damage")
    void testInsuranceCoverage() {
        LocalDate start = LocalDate.now();
        LocalDate end = start.plusDays(3);
        
        Reservation reservation = service.makeReservation(customer, car, start, end, InsuranceType.PREMIUM);
        
        service.pickupVehicle(reservation);
        DamageReport damage = service.reportDamage(car, "Dent", DamageSeverity.MODERATE);
        service.returnVehicle(reservation, 100, damage, end);
        
        // Premium insurance covers 100% of damage
        assertEquals(0, reservation.getDamageCost());
    }

    @Test
    @DisplayName("Cancel reservation releases vehicle")
    void testCancelReservation() {
        LocalDate start = LocalDate.now();
        LocalDate end = start.plusDays(3);
        
        Reservation reservation = service.makeReservation(customer, car, start, end, InsuranceType.NONE);
        service.cancelReservation(reservation);
        
        assertEquals(ReservationStatus.CANCELLED, reservation.getStatus());
        assertTrue(car.isAvailable());
    }

    @Test
    @DisplayName("Concurrent reservations are thread-safe")
    void testConcurrentReservations() throws InterruptedException {
        LocalDate start = LocalDate.now();
        LocalDate end = start.plusDays(3);
        
        ExecutorService executor = Executors.newFixedThreadPool(10);
        CountDownLatch latch = new CountDownLatch(10);
        ConcurrentLinkedQueue<Boolean> results = new ConcurrentLinkedQueue<>();
        
        for (int i = 0; i < 10; i++) {
            final int idx = i;
            executor.submit(() -> {
                try {
                    Customer c = service.registerCustomer("T" + idx, "Test" + idx, "t@test.com", "555", "DL");
                    service.makeReservation(c, car, start, end, InsuranceType.NONE);
                    results.add(true);
                } catch (Exception e) {
                    results.add(false);
                } finally {
                    latch.countDown();
                }
            });
        }
        
        latch.await(5, TimeUnit.SECONDS);
        executor.shutdown();
        
        // Only one should succeed
        long successCount = results.stream().filter(b -> b).count();
        assertEquals(1, successCount);
    }

    @Test
    @DisplayName("Surge pricing increases cost")
    void testSurgePricing() {
        LocalDate start = LocalDate.now();
        LocalDate end = start.plusDays(3);
        
        // Normal price
        Reservation normalRes = service.makeReservation(customer, car, start, end, InsuranceType.NONE);
        double normalCost = normalRes.getRentalCost();
        service.cancelReservation(normalRes);
        
        // Enable surge pricing
        service.updateDemand(VehicleType.CAR, 2.0);
        
        Reservation surgeRes = service.makeReservation(customer, car, start, end, InsuranceType.NONE);
        double surgeCost = surgeRes.getRentalCost();
        
        assertTrue(surgeCost > normalCost);
    }

    @Test
    @DisplayName("Loyalty points awarded on completion")
    void testLoyaltyPoints() {
        LocalDate start = LocalDate.now();
        LocalDate end = start.plusDays(3);
        
        Reservation reservation = service.makeReservation(customer, car, start, end, InsuranceType.NONE);
        service.pickupVehicle(reservation);
        service.returnVehicle(reservation, 100, null, end);
        
        assertTrue(customer.getLoyaltyPoints() > 0);
    }
}
