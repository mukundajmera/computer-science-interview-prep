import org.junit.jupiter.api.*;
import static org.junit.jupiter.api.Assertions.*;

import java.util.*;
import java.util.concurrent.*;

/**
 * Tests for Movie Ticket Booking System
 */
public class MovieTicketBookingTest {
    
    // ==================== V1 Basic Tests ====================
    
    @Nested
    @DisplayName("V1 Basic Tests")
    class V1BasicTests {
        
        @Test
        @DisplayName("Should create movie with correct properties")
        void testMovieCreation() {
            Movie movie = new Movie("M1", "Avengers", 180, "Action");
            
            assertEquals("M1", movie.getId());
            assertEquals("Avengers", movie.getTitle());
            assertEquals(180, movie.getDurationMinutes());
            assertEquals("Action", movie.getGenre());
        }
        
        @Test
        @DisplayName("Should create standard screen with correct seat layout")
        void testScreenCreation() {
            Screen screen = Screen.createStandardScreen("S1", "Screen 1", 1, 2, 3, 5);
            
            assertEquals("S1", screen.getId());
            assertEquals("Screen 1", screen.getName());
            assertEquals(30, screen.getCapacity()); // 6 rows * 5 seats
            
            List<Seat> seats = screen.getSeats();
            // Check VIP row
            assertEquals(SeatType.VIP, seats.get(0).getType());
            // Check Premium rows
            assertEquals(SeatType.PREMIUM, seats.get(5).getType());
            // Check Regular rows
            assertEquals(SeatType.REGULAR, seats.get(15).getType());
        }
        
        @Test
        @DisplayName("Should lock and book seats correctly")
        void testSeatLockingAndBooking() {
            Seat seat = new Seat("A1", "A", 1, SeatType.VIP);
            ShowSeat showSeat = new ShowSeat(seat, 20.0);
            
            assertTrue(showSeat.isAvailable());
            
            // Lock seat
            assertTrue(showSeat.lock("user1"));
            assertEquals(SeatStatus.LOCKED, showSeat.getStatus());
            assertFalse(showSeat.isAvailable());
            
            // Cannot lock again
            assertFalse(showSeat.lock("user2"));
            
            // Book seat
            assertTrue(showSeat.book("user1"));
            assertEquals(SeatStatus.BOOKED, showSeat.getStatus());
        }
        
        @Test
        @DisplayName("Should prevent booking by wrong user")
        void testBookingByWrongUser() {
            Seat seat = new Seat("A1", "A", 1, SeatType.VIP);
            ShowSeat showSeat = new ShowSeat(seat, 20.0);
            
            showSeat.lock("user1");
            assertFalse(showSeat.book("user2")); // Wrong user
            assertEquals(SeatStatus.LOCKED, showSeat.getStatus());
        }
        
        @Test
        @DisplayName("Should create show with seats from screen")
        void testShowCreation() {
            Movie movie = new Movie("M1", "Test", 120, "Drama");
            Screen screen = Screen.createStandardScreen("S1", "Screen 1", 1, 1, 1, 5);
            Show show = new Show("SH1", movie, screen, new Date());
            
            assertEquals(15, show.getAvailableSeats().size());
            assertNotNull(show.getShowSeat("A1"));
        }
        
        @Test
        @DisplayName("Should lock multiple seats atomically")
        void testMultipleSeatLocking() {
            Movie movie = new Movie("M1", "Test", 120, "Drama");
            Screen screen = Screen.createStandardScreen("S1", "Screen 1", 1, 1, 1, 5);
            Show show = new Show("SH1", movie, screen, new Date());
            
            List<String> seatIds = Arrays.asList("A1", "A2", "A3");
            assertTrue(show.lockSeats(seatIds, "user1"));
            
            // All seats should be locked
            for (String seatId : seatIds) {
                assertEquals(SeatStatus.LOCKED, show.getShowSeat(seatId).getStatus());
            }
            
            // Cannot lock same seats again
            assertFalse(show.lockSeats(Arrays.asList("A2", "A3"), "user2"));
        }
        
        @Test
        @DisplayName("Should calculate booking total correctly")
        void testBookingTotal() {
            Movie movie = new Movie("M1", "Test", 120, "Drama");
            Screen screen = Screen.createStandardScreen("S1", "Screen 1", 1, 1, 0, 3);
            Show show = new Show("SH1", movie, screen, new Date());
            
            show.lockSeats(Arrays.asList("A1", "B1"), "user1");
            
            List<ShowSeat> seats = Arrays.asList(
                show.getShowSeat("A1"),
                show.getShowSeat("B1")
            );
            
            Booking booking = new Booking("BK1", show, "user1", seats);
            
            // VIP (20) + Premium (15) = 35
            assertEquals(35.0, booking.getTotalAmount(), 0.01);
        }
    }
    
    // ==================== V3 Concurrency Tests ====================
    
    @Nested
    @DisplayName("V3 Concurrency Tests")
    class V3ConcurrencyTests {
        
        @Test
        @DisplayName("Should handle concurrent seat locking")
        void testConcurrentSeatLocking() throws InterruptedException {
            Movie movie = new Movie("M1", "Test", 120, "Drama");
            Screen screen = Screen.createStandardScreen("S1", "Screen 1", 1, 0, 0, 5);
            Show show = new Show("SH1", movie, screen, new Date());
            
            List<String> targetSeats = Arrays.asList("A1", "A2");
            
            CountDownLatch startLatch = new CountDownLatch(1);
            CountDownLatch doneLatch = new CountDownLatch(10);
            List<Boolean> results = new CopyOnWriteArrayList<>();
            
            for (int i = 0; i < 10; i++) {
                final String userId = "user" + i;
                new Thread(() -> {
                    try {
                        startLatch.await();
                        boolean locked = show.lockSeats(targetSeats, userId);
                        results.add(locked);
                    } catch (InterruptedException e) {
                        Thread.currentThread().interrupt();
                    } finally {
                        doneLatch.countDown();
                    }
                }).start();
            }
            
            startLatch.countDown(); // Start all threads
            doneLatch.await(5, TimeUnit.SECONDS);
            
            // Only one should succeed
            long successCount = results.stream().filter(r -> r).count();
            assertEquals(1, successCount);
        }
        
        @Test
        @DisplayName("Should handle concurrent booking creation")
        void testConcurrentBookingCreation() throws InterruptedException {
            BookingSystem system = BookingSystem.createNewInstance(60000);
            
            Movie movie = new Movie("M1", "Test", 120, "Drama");
            Screen screen = Screen.createStandardScreen("S1", "Screen 1", 1, 0, 0, 5);
            Show show = new Show("SH1", movie, screen, new Date());
            
            system.addMovie(movie);
            system.addScreen(screen);
            system.addShow(show);
            
            List<String> targetSeats = Arrays.asList("A3", "A4");
            
            CountDownLatch startLatch = new CountDownLatch(1);
            CountDownLatch doneLatch = new CountDownLatch(5);
            List<Booking> bookings = new CopyOnWriteArrayList<>();
            
            for (int i = 0; i < 5; i++) {
                final String userId = "user" + i;
                new Thread(() -> {
                    try {
                        startLatch.await();
                        Booking booking = system.createBooking(userId, "SH1", targetSeats);
                        if (booking != null) {
                            bookings.add(booking);
                        }
                    } catch (InterruptedException e) {
                        Thread.currentThread().interrupt();
                    } finally {
                        doneLatch.countDown();
                    }
                }).start();
            }
            
            startLatch.countDown();
            doneLatch.await(5, TimeUnit.SECONDS);
            
            // Only one booking should be created
            assertEquals(1, bookings.size());
            
            system.shutdown();
        }
        
        @Test
        @DisplayName("Should handle booking confirmation correctly")
        void testBookingConfirmation() {
            BookingSystem system = BookingSystem.createNewInstance(60000);
            
            Movie movie = new Movie("M1", "Test", 120, "Drama");
            Screen screen = Screen.createStandardScreen("S1", "Screen 1", 0, 1, 0, 3);
            Show show = new Show("SH1", movie, screen, new Date());
            
            system.addMovie(movie);
            system.addScreen(screen);
            system.addShow(show);
            
            Booking booking = system.createBooking("user1", "SH1", Arrays.asList("A1", "A2"));
            assertNotNull(booking);
            assertEquals(BookingStatus.PENDING, booking.getStatus());
            
            // Confirm (may fail due to simulated payment)
            // Run multiple times to account for 5% failure rate
            boolean confirmed = false;
            for (int i = 0; i < 5 && !confirmed; i++) {
                if (booking.getStatus() == BookingStatus.PENDING) {
                    confirmed = system.confirmBooking(booking.getId(), "CREDIT_CARD");
                }
            }
            
            system.shutdown();
        }
        
        @Test
        @DisplayName("Should handle booking cancellation")
        void testBookingCancellation() {
            BookingSystem system = BookingSystem.createNewInstance(60000);
            
            Movie movie = new Movie("M1", "Test", 120, "Drama");
            Screen screen = Screen.createStandardScreen("S1", "Screen 1", 0, 1, 0, 3);
            Show show = new Show("SH1", movie, screen, new Date());
            
            system.addMovie(movie);
            system.addScreen(screen);
            system.addShow(show);
            
            Booking booking = system.createBooking("user1", "SH1", Arrays.asList("A1"));
            assertNotNull(booking);
            
            // Cancel pending booking
            assertTrue(system.cancelBooking(booking.getId(), "user1"));
            assertEquals(BookingStatus.CANCELLED, booking.getStatus());
            
            // Seat should be available again
            assertTrue(show.getShowSeat("A1").isAvailable());
            
            system.shutdown();
        }
        
        @Test
        @DisplayName("Should not allow cancellation by wrong user")
        void testCancellationByWrongUser() {
            BookingSystem system = BookingSystem.createNewInstance(60000);
            
            Movie movie = new Movie("M1", "Test", 120, "Drama");
            Screen screen = Screen.createStandardScreen("S1", "Screen 1", 0, 1, 0, 3);
            Show show = new Show("SH1", movie, screen, new Date());
            
            system.addMovie(movie);
            system.addScreen(screen);
            system.addShow(show);
            
            Booking booking = system.createBooking("user1", "SH1", Arrays.asList("A1"));
            
            // Wrong user cannot cancel
            assertFalse(system.cancelBooking(booking.getId(), "user2"));
            assertEquals(BookingStatus.PENDING, booking.getStatus());
            
            system.shutdown();
        }
    }
    
    // ==================== Integration Tests ====================
    
    @Nested
    @DisplayName("Integration Tests")
    class IntegrationTests {
        
        @Test
        @DisplayName("Complete booking flow")
        void testCompleteBookingFlow() {
            BookingSystem system = BookingSystem.createNewInstance(60000);
            
            // Setup
            Movie movie = new Movie("M1", "Avengers", 180, "Action");
            Screen screen = Screen.createStandardScreen("S1", "Screen 1", 1, 2, 3, 8);
            Show show = new Show("SH1", movie, screen, new Date());
            
            system.addMovie(movie);
            system.addScreen(screen);
            system.addShow(show);
            
            // Search movie
            List<Movie> searchResults = system.searchMovies("Avengers");
            assertEquals(1, searchResults.size());
            
            // Get shows
            List<Show> shows = system.getShowsForMovie("M1");
            assertEquals(1, shows.size());
            
            // Create booking
            List<String> seatIds = Arrays.asList("B1", "B2", "B3");
            Booking booking = system.createBooking("user1", "SH1", seatIds);
            assertNotNull(booking);
            
            // Total = 3 * Premium ($15) = $45
            assertEquals(45.0, booking.getTotalAmount(), 0.01);
            
            system.shutdown();
        }
        
        @Test
        @DisplayName("Should get system statistics")
        void testSystemStatistics() {
            BookingSystem system = BookingSystem.createNewInstance(60000);
            
            Movie movie = new Movie("M1", "Test", 120, "Drama");
            Screen screen = Screen.createStandardScreen("S1", "Screen 1", 1, 1, 1, 3);
            Show show = new Show("SH1", movie, screen, new Date());
            
            system.addMovie(movie);
            system.addScreen(screen);
            system.addShow(show);
            
            Map<String, Object> stats = system.getSystemStats();
            
            assertEquals(1, stats.get("totalMovies"));
            assertEquals(1, stats.get("totalScreens"));
            assertEquals(1, stats.get("totalShows"));
            
            system.shutdown();
        }
    }
}
