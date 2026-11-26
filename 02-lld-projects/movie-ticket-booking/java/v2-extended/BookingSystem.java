import java.util.*;

/**
 * Movie Ticket Booking System - V1 Basic
 * 
 * Main BookingSystem class.
 */

class BookingSystem {
    private final Map<String, Movie> movies;
    private final Map<String, Screen> screens;
    private final Map<String, Show> shows;
    private final Map<String, Booking> bookings;
    private int bookingCounter;
    
    public BookingSystem() {
        this.movies = new HashMap<>();
        this.screens = new HashMap<>();
        this.shows = new HashMap<>();
        this.bookings = new HashMap<>();
        this.bookingCounter = 0;
    }
    
    // ============ Movie Management ============
    
    public void addMovie(Movie movie) {
        movies.put(movie.getId(), movie);
        System.out.println("Added movie: " + movie.getTitle());
    }
    
    public Movie getMovie(String movieId) {
        return movies.get(movieId);
    }
    
    public List<Movie> getAllMovies() {
        return new ArrayList<>(movies.values());
    }
    
    // ============ Screen Management ============
    
    public void addScreen(Screen screen) {
        screens.put(screen.getId(), screen);
        System.out.println("Added screen: " + screen.getName() + " with " + screen.getCapacity() + " seats");
    }
    
    public Screen getScreen(String screenId) {
        return screens.get(screenId);
    }
    
    // ============ Show Management ============
    
    public Show createShow(String showId, Movie movie, Screen screen, Date startTime) {
        Show show = new Show(showId, movie, screen, startTime);
        shows.put(showId, show);
        System.out.println("Created show: " + show);
        return show;
    }
    
    public Show getShow(String showId) {
        return shows.get(showId);
    }
    
    public List<Show> getShowsForMovie(String movieId) {
        List<Show> movieShows = new ArrayList<>();
        for (Show show : shows.values()) {
            if (show.getMovie().getId().equals(movieId)) {
                movieShows.add(show);
            }
        }
        return movieShows;
    }
    
    // ============ Booking Operations ============
    
    /**
     * Lock seats for a user (first step of booking).
     */
    public boolean lockSeats(String showId, List<String> seatIds, String userId) {
        Show show = shows.get(showId);
        if (show == null) {
            System.out.println("Show not found: " + showId);
            return false;
        }
        
        boolean locked = show.lockSeats(seatIds, userId);
        if (locked) {
            System.out.println("Seats locked for " + userId + ": " + seatIds);
        } else {
            System.out.println("Failed to lock seats - some may be unavailable");
        }
        return locked;
    }
    
    /**
     * Create a booking after seats are locked.
     */
    public Booking createBooking(String showId, List<String> seatIds, String userId) {
        Show show = shows.get(showId);
        if (show == null) {
            System.out.println("Show not found");
            return null;
        }
        
        // Get ShowSeats for the booking
        List<ShowSeat> bookingSeats = new ArrayList<>();
        for (String seatId : seatIds) {
            ShowSeat showSeat = show.getShowSeat(seatId);
            if (showSeat == null || showSeat.getStatus() != SeatStatus.LOCKED || 
                !userId.equals(showSeat.getLockedBy())) {
                System.out.println("Seat " + seatId + " is not locked by this user");
                return null;
            }
            bookingSeats.add(showSeat);
        }
        
        String bookingId = "BK" + (++bookingCounter);
        Booking booking = new Booking(bookingId, show, userId, bookingSeats);
        bookings.put(bookingId, booking);
        
        System.out.println("Booking created: " + bookingId);
        return booking;
    }
    
    /**
     * Add snack concession package to a pending booking.
     */
    public boolean addSnackToBooking(String bookingId, SnackConcession snack) {
        Booking booking = bookings.get(bookingId);
        if (booking == null) {
            System.out.println("Booking not found: " + bookingId);
            return false;
        }
        if (booking.getStatus() != BookingStatus.PENDING) {
            System.out.println("Cannot add snacks to non-pending booking: " + bookingId);
            return false;
        }
        booking.addSnack(snack);
        System.out.println("Added " + snack.getDisplayName() + " to booking " + bookingId);
        return true;
    }

    /**
     * Confirm booking (mark seats as booked).
     */
    public boolean confirmBooking(String bookingId) {
        Booking booking = bookings.get(bookingId);
        if (booking == null) {
            System.out.println("Booking not found");
            return false;
        }
        
        // Book all seats
        List<String> seatIds = new ArrayList<>();
        for (ShowSeat seat : booking.getSeats()) {
            seatIds.add(seat.getSeat().getId());
        }
        
        boolean booked = booking.getShow().bookSeats(seatIds, booking.getUserId());
        if (booked) {
            booking.confirm();
            System.out.println("Booking confirmed: " + bookingId);
            printTicket(booking);
            return true;
        }
        
        return false;
    }
    
    /**
     * Cancel a booking.
     */
    public boolean cancelBooking(String bookingId) {
        Booking booking = bookings.get(bookingId);
        if (booking == null) {
            System.out.println("Booking not found");
            return false;
        }
        
        booking.cancel();
        System.out.println("Booking cancelled: " + bookingId);
        return true;
    }
    
    /**
     * Get booking by ID.
     */
    public Booking getBooking(String bookingId) {
        return bookings.get(bookingId);
    }
    
    /**
     * Print ticket for a confirmed booking.
     */
    public void printTicket(Booking booking) {
        System.out.println("\n========== TICKET ==========");
        System.out.println(booking);
        System.out.println("============================\n");
    }
    
    /**
     * Display available shows for a movie.
     */
    public void displayShows(String movieId) {
        List<Show> movieShows = getShowsForMovie(movieId);
        if (movieShows.isEmpty()) {
            System.out.println("No shows available for this movie");
            return;
        }
        
        System.out.println("\n=== Available Shows ===");
        for (Show show : movieShows) {
            long available = show.getAvailableSeats().size();
            System.out.println(show + " - " + available + " seats available");
        }
    }
}
