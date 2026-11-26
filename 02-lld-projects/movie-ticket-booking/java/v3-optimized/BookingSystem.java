import java.util.ArrayList;
import java.util.Date;
import java.util.HashMap;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

/**
 * Movie Ticket Booking System - V3 Optimized
 *
 * Backward-compatible API with explicit lifecycle and stats hooks.
 */
class BookingSystem {
    private static final Object INSTANCE_LOCK = new Object();
    private static BookingSystem instance;

    private final Object stateLock;
    private final Map<String, Movie> movies;
    private final Map<String, Screen> screens;
    private final Map<String, Show> shows;
    private final Map<String, Booking> bookings;
    private int bookingCounter;

    public BookingSystem() {
        this.stateLock = new Object();
        this.movies = new HashMap<String, Movie>();
        this.screens = new HashMap<String, Screen>();
        this.shows = new HashMap<String, Show>();
        this.bookings = new HashMap<String, Booking>();
        this.bookingCounter = 0;
    }

    public static BookingSystem createNewInstance(long bookingExpirationMs) {
        synchronized (INSTANCE_LOCK) {
            ShowSeat.setLockTimeoutMs(bookingExpirationMs);
            instance = new BookingSystem();
            return instance;
        }
    }

    public static BookingSystem getInstance() {
        synchronized (INSTANCE_LOCK) {
            if (instance == null) {
                instance = new BookingSystem();
            }
            return instance;
        }
    }

    public static void resetInstance() {
        synchronized (INSTANCE_LOCK) {
            instance = null;
        }
    }

    // ============ Movie Management ============

    public void addMovie(Movie movie) {
        if (movie == null) {
            return;
        }
        synchronized (stateLock) {
            movies.put(movie.getId(), movie);
        }
    }

    public Movie getMovie(String movieId) {
        synchronized (stateLock) {
            return movies.get(movieId);
        }
    }

    public List<Movie> getAllMovies() {
        synchronized (stateLock) {
            return new ArrayList<Movie>(movies.values());
        }
    }

    public List<Movie> searchMovies(String query) {
        String normalized = query == null ? "" : query.trim().toLowerCase();
        synchronized (stateLock) {
            List<Movie> result = new ArrayList<Movie>();
            for (Movie movie : movies.values()) {
                if (normalized.isEmpty()) {
                    result.add(movie);
                    continue;
                }
                String title = movie.getTitle() == null ? "" : movie.getTitle().toLowerCase();
                String genre = movie.getGenre() == null ? "" : movie.getGenre().toLowerCase();
                if (title.contains(normalized) || genre.contains(normalized)) {
                    result.add(movie);
                }
            }
            return result;
        }
    }

    // ============ Screen Management ============

    public void addScreen(Screen screen) {
        if (screen == null) {
            return;
        }
        synchronized (stateLock) {
            screens.put(screen.getId(), screen);
        }
    }

    public Screen getScreen(String screenId) {
        synchronized (stateLock) {
            return screens.get(screenId);
        }
    }

    // ============ Show Management ============

    public Show createShow(String showId, Movie movie, Screen screen, Date startTime) {
        Show show = new Show(showId, movie, screen, startTime);
        addShow(show);
        return show;
    }

    public void addShow(Show show) {
        if (show == null) {
            return;
        }
        synchronized (stateLock) {
            shows.put(show.getId(), show);
        }
    }

    public Show getShow(String showId) {
        synchronized (stateLock) {
            return shows.get(showId);
        }
    }

    public List<Show> getShowsForMovie(String movieId) {
        synchronized (stateLock) {
            List<Show> result = new ArrayList<Show>();
            for (Show show : shows.values()) {
                if (show.getMovie().getId().equals(movieId)) {
                    result.add(show);
                }
            }
            return result;
        }
    }

    // ============ Booking Operations ============

    public boolean lockSeats(String showId, List<String> seatIds, String userId) {
        synchronized (stateLock) {
            Show show = shows.get(showId);
            if (show == null || seatIds == null || seatIds.isEmpty() || userId == null || userId.isEmpty()) {
                return false;
            }
            return show.lockSeats(seatIds, userId);
        }
    }

    public Booking createBooking(String userId, String showId, List<String> seatIds) {
        synchronized (stateLock) {
            Show show = shows.get(showId);
            if (show == null || seatIds == null || seatIds.isEmpty() || userId == null || userId.isEmpty()) {
                return null;
            }

            if (!areSeatsLockedByUser(show, seatIds, userId) && !show.lockSeats(seatIds, userId)) {
                return null;
            }

            List<ShowSeat> bookingSeats = new ArrayList<ShowSeat>();
            for (String seatId : seatIds) {
                ShowSeat showSeat = show.getShowSeat(seatId);
                if (showSeat == null) {
                    show.unlockSeats(seatIds);
                    return null;
                }
                bookingSeats.add(showSeat);
            }

            String bookingId = "BK" + (++bookingCounter);
            Booking booking = new Booking(bookingId, show, userId, bookingSeats);
            bookings.put(bookingId, booking);
            return booking;
        }
    }

    // Backward-compatible overload retained for existing demos.
    public Booking createBooking(String showId, List<String> seatIds, String userId) {
        return createBooking(userId, showId, seatIds);
    }

    public boolean confirmBooking(String bookingId, String paymentMethod) {
        synchronized (stateLock) {
            Booking booking = bookings.get(bookingId);
            if (booking == null || booking.getStatus() != BookingStatus.PENDING) {
                return false;
            }
            if (paymentMethod == null || paymentMethod.trim().isEmpty()) {
                return false;
            }

            boolean booked = booking.getShow().bookSeats(booking.getSeatIds(), booking.getUserId());
            if (!booked) {
                return false;
            }

            booking.confirm();
            return true;
        }
    }

    // Backward-compatible overload retained for existing demos.
    public boolean confirmBooking(String bookingId) {
        return confirmBooking(bookingId, "DEFAULT");
    }

    public boolean cancelBooking(String bookingId, String userId) {
        synchronized (stateLock) {
            Booking booking = bookings.get(bookingId);
            if (booking == null || userId == null || !userId.equals(booking.getUserId())) {
                return false;
            }
            if (booking.getStatus() == BookingStatus.CONFIRMED) {
                return false;
            }
            if (booking.getStatus() == BookingStatus.CANCELLED) {
                return true;
            }
            booking.cancel();
            return true;
        }
    }

    // Backward-compatible overload retained for existing demos.
    public boolean cancelBooking(String bookingId) {
        synchronized (stateLock) {
            Booking booking = bookings.get(bookingId);
            if (booking == null || booking.getStatus() == BookingStatus.CONFIRMED) {
                return false;
            }
            if (booking.getStatus() == BookingStatus.CANCELLED) {
                return true;
            }
            booking.cancel();
            return true;
        }
    }

    public Booking getBooking(String bookingId) {
        synchronized (stateLock) {
            return bookings.get(bookingId);
        }
    }

    public List<Booking> getUserBookings(String userId) {
        synchronized (stateLock) {
            List<Booking> result = new ArrayList<Booking>();
            for (Booking booking : bookings.values()) {
                if (booking.getUserId().equals(userId)) {
                    result.add(booking);
                }
            }
            return result;
        }
    }

    public Map<String, Object> getSystemStats() {
        synchronized (stateLock) {
            Map<String, Object> stats = new LinkedHashMap<String, Object>();
            stats.put("totalMovies", movies.size());
            stats.put("totalScreens", screens.size());
            stats.put("totalShows", shows.size());
            stats.put("totalBookings", bookings.size());
            return stats;
        }
    }

    public void shutdown() {
        synchronized (stateLock) {
            movies.clear();
            screens.clear();
            shows.clear();
            bookings.clear();
            bookingCounter = 0;
        }
        synchronized (INSTANCE_LOCK) {
            if (instance == this) {
                instance = null;
            }
        }
    }

    public void printTicket(Booking booking) {
        if (booking == null) {
            return;
        }
        System.out.println("\n========== TICKET ==========");
        System.out.println(booking);
        System.out.println("============================\n");
    }

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

    private boolean areSeatsLockedByUser(Show show, List<String> seatIds, String userId) {
        for (String seatId : seatIds) {
            ShowSeat showSeat = show.getShowSeat(seatId);
            if (showSeat == null) {
                return false;
            }
            if (showSeat.getStatus() != SeatStatus.LOCKED || !userId.equals(showSeat.getLockedBy())) {
                return false;
            }
        }
        return true;
    }
}
