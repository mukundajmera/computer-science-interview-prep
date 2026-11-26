import java.util.*;

/**
 * Movie Ticket Booking System - V2 Extended Demo
 * Demonstrates:
 * 1. Tiered seating (VIP, Premium, Regular) with differentiated pricing.
 * 2. Concession add-on packages (SnackConcession).
 * 3. Itemized receipt calculation with seat totals and snacks.
 */
public class MovieTicketBookingDemo {
    
    public static void main(String[] args) {
        System.out.println("=============================================");
        System.out.println("   Movie Ticket Booking System - V2 Extended");
        System.out.println("=============================================\n");
        
        BookingSystem system = new BookingSystem();
        
        // Setup movies
        Movie avengers = new Movie("M1", "Avengers: Endgame", 180, "Action");
        Movie inception = new Movie("M2", "Inception", 148, "Sci-Fi");
        system.addMovie(avengers);
        system.addMovie(inception);
        
        // Setup screens with tiered seating (VIP, Premium, Regular)
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
        
        // Display seat map with tiers
        show1.displaySeats();
        
        // Demo 1: Successful booking for regular seats
        System.out.println("\n--- Demo 1: Book Regular Seats B2, B3 ---");
        List<String> selectedSeats = Arrays.asList("B2", "B3");
        
        if (system.lockSeats("SH1", selectedSeats, "user1")) {
            Booking booking = system.createBooking("SH1", selectedSeats, "user1");
            if (booking != null) {
                system.confirmBooking(booking.getId());
            }
        }
        
        // Show updated seat map
        show1.displaySeats();
        
        // Demo 2: Conflict handling - try to book same seats
        System.out.println("\n--- Demo 2: Try to book B2, B3 again (should fail) ---");
        if (!system.lockSeats("SH1", selectedSeats, "user2")) {
            System.out.println("Cannot book - seats already taken!");
        }
        
        // Demo 3: Book VIP seats with Snack Concession Packages
        System.out.println("\n--- Demo 3: Book VIP seats A1, A2 with Snack Concession Add-ons ---");
        List<String> vipSeats = Arrays.asList("A1", "A2");
        
        if (system.lockSeats("SH1", vipSeats, "user2")) {
            Booking booking2 = system.createBooking("SH1", vipSeats, "user2");
            if (booking2 != null) {
                System.out.println("\nAdding Snack Concessions to Booking " + booking2.getId() + "...");
                system.addSnackToBooking(booking2.getId(), SnackConcession.COMBO_MEAL);
                system.addSnackToBooking(booking2.getId(), SnackConcession.NACHOS);
                
                System.out.println("\nConfirming booking with snack packages:");
                system.confirmBooking(booking2.getId());
            }
        }
        
        // Final seat map
        show1.displaySeats();
        
        System.out.println("\n--- V2 Extended Demo Complete ---");
    }
}
