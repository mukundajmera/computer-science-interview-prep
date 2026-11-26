import java.util.*;

/**
 * Movie Ticket Booking System - V1 Basic Demo
 */
public class MovieTicketBookingDemo {
    
    public static void main(String[] args) {
        System.out.println("=============================================");
        System.out.println("   Movie Ticket Booking System - V1 Basic");
        System.out.println("=============================================\n");
        
        BookingSystem system = new BookingSystem();
        
        // Setup movies
        Movie avengers = new Movie("M1", "Avengers: Endgame", 180, "Action");
        Movie inception = new Movie("M2", "Inception", 148, "Sci-Fi");
        system.addMovie(avengers);
        system.addMovie(inception);
        
        // Setup screens
        Screen screen1 = Screen.createStandardScreen("S1", "Screen 1", 2, 3, 3, 5);
        system.addScreen(screen1);
        
        // Create shows
        Calendar cal = Calendar.getInstance();
        cal.set(2024, Calendar.JANUARY, 15, 18, 0);
        Show show1 = system.createShow("SH1", avengers, screen1, cal.getTime());
        
        cal.set(2024, Calendar.JANUARY, 15, 21, 0);
        Show show2 = system.createShow("SH2", avengers, screen1, cal.getTime());
        
        // Display available shows
        system.displayShows("M1");
        
        // Display seat map
        show1.displaySeats();
        
        // Demo 1: Successful booking
        System.out.println("\n--- Demo 1: Book Seats B2, B3 ---");
        List<String> selectedSeats = Arrays.asList("B2", "B3");
        
        if (system.lockSeats("SH1", selectedSeats, "user1")) {
            Booking booking = system.createBooking("SH1", selectedSeats, "user1");
            if (booking != null) {
                system.confirmBooking(booking.getId());
            }
        }
        
        // Show updated seat map
        show1.displaySeats();
        
        // Demo 2: Try to book same seats (should fail)
        System.out.println("\n--- Demo 2: Try to book B2, B3 again (should fail) ---");
        if (!system.lockSeats("SH1", selectedSeats, "user2")) {
            System.out.println("Cannot book - seats already taken!");
        }
        
        // Demo 3: Book different seats
        System.out.println("\n--- Demo 3: Book seats A1, A2 (VIP) ---");
        List<String> vipSeats = Arrays.asList("A1", "A2");
        
        if (system.lockSeats("SH1", vipSeats, "user2")) {
            Booking booking2 = system.createBooking("SH1", vipSeats, "user2");
            if (booking2 != null) {
                system.confirmBooking(booking2.getId());
            }
        }
        
        // Final seat map
        show1.displaySeats();
        
        System.out.println("\n--- Demo Complete ---");
    }
}
