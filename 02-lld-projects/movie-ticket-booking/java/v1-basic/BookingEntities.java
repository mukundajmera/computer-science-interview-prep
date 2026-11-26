import java.util.*;

/**
 * Movie Ticket Booking System - V1 Basic
 * 
 * Core entities for the booking system.
 */

enum SeatType {
    REGULAR(10.0),
    PREMIUM(15.0),
    VIP(20.0);
    
    private final double basePrice;
    
    SeatType(double basePrice) {
        this.basePrice = basePrice;
    }
    
    public double getBasePrice() {
        return basePrice;
    }
}

enum SeatStatus {
    AVAILABLE,
    LOCKED,
    BOOKED
}

enum BookingStatus {
    PENDING,
    CONFIRMED,
    CANCELLED
}

/**
 * Represents a movie.
 */
class Movie {
    private final String id;
    private final String title;
    private final int durationMinutes;
    private final String genre;
    
    public Movie(String id, String title, int durationMinutes, String genre) {
        this.id = id;
        this.title = title;
        this.durationMinutes = durationMinutes;
        this.genre = genre;
    }
    
    public String getId() { return id; }
    public String getTitle() { return title; }
    public int getDurationMinutes() { return durationMinutes; }
    public String getGenre() { return genre; }
    
    @Override
    public String toString() {
        return title + " (" + genre + ", " + durationMinutes + " min)";
    }
}

/**
 * Represents a physical seat in a screen.
 */
class Seat {
    private final String id;
    private final String row;
    private final int number;
    private final SeatType type;
    
    public Seat(String id, String row, int number, SeatType type) {
        this.id = id;
        this.row = row;
        this.number = number;
        this.type = type;
    }
    
    public String getId() { return id; }
    public String getRow() { return row; }
    public int getNumber() { return number; }
    public SeatType getType() { return type; }
    
    @Override
    public String toString() {
        return row + number;
    }
}

/**
 * Represents a seat's availability for a specific show.
 */
class ShowSeat {
    private final Seat seat;
    private SeatStatus status;
    private double price;
    private String lockedBy;
    private long lockedAt;
    private static final long LOCK_TIMEOUT_MS = 10 * 60 * 1000; // 10 minutes
    
    public ShowSeat(Seat seat, double price) {
        this.seat = seat;
        this.price = price;
        this.status = SeatStatus.AVAILABLE;
        this.lockedBy = null;
        this.lockedAt = 0;
    }
    
    public Seat getSeat() { return seat; }
    public SeatStatus getStatus() { return status; }
    public double getPrice() { return price; }
    public String getLockedBy() { return lockedBy; }
    
    public boolean isAvailable() {
        if (status == SeatStatus.LOCKED && isLockExpired()) {
            unlock();
        }
        return status == SeatStatus.AVAILABLE;
    }
    
    public boolean isLockExpired() {
        return System.currentTimeMillis() - lockedAt > LOCK_TIMEOUT_MS;
    }
    
    public boolean lock(String userId) {
        if (isAvailable()) {
            this.status = SeatStatus.LOCKED;
            this.lockedBy = userId;
            this.lockedAt = System.currentTimeMillis();
            return true;
        }
        return false;
    }
    
    public void unlock() {
        this.status = SeatStatus.AVAILABLE;
        this.lockedBy = null;
        this.lockedAt = 0;
    }
    
    public boolean book(String userId) {
        if (status == SeatStatus.LOCKED && lockedBy.equals(userId)) {
            this.status = SeatStatus.BOOKED;
            return true;
        }
        return false;
    }
    
    @Override
    public String toString() {
        String statusMark = switch (status) {
            case AVAILABLE -> "[ ]";
            case LOCKED -> "[L]";
            case BOOKED -> "[X]";
        };
        return seat.toString() + statusMark;
    }
}

/**
 * Represents a screen in a theater.
 */
class Screen {
    private final String id;
    private final String name;
    private final List<Seat> seats;
    
    public Screen(String id, String name) {
        this.id = id;
        this.name = name;
        this.seats = new ArrayList<>();
    }
    
    public void addSeat(Seat seat) {
        seats.add(seat);
    }
    
    public String getId() { return id; }
    public String getName() { return name; }
    public List<Seat> getSeats() { return new ArrayList<>(seats); }
    public int getCapacity() { return seats.size(); }
    
    /**
     * Create a standard screen with rows of seats.
     */
    public static Screen createStandardScreen(String id, String name, 
                                              int vipRows, int premiumRows, int regularRows, 
                                              int seatsPerRow) {
        Screen screen = new Screen(id, name);
        char rowChar = 'A';
        
        for (int r = 0; r < vipRows; r++) {
            String row = String.valueOf(rowChar++);
            for (int s = 1; s <= seatsPerRow; s++) {
                screen.addSeat(new Seat(row + s, row, s, SeatType.VIP));
            }
        }
        
        for (int r = 0; r < premiumRows; r++) {
            String row = String.valueOf(rowChar++);
            for (int s = 1; s <= seatsPerRow; s++) {
                screen.addSeat(new Seat(row + s, row, s, SeatType.PREMIUM));
            }
        }
        
        for (int r = 0; r < regularRows; r++) {
            String row = String.valueOf(rowChar++);
            for (int s = 1; s <= seatsPerRow; s++) {
                screen.addSeat(new Seat(row + s, row, s, SeatType.REGULAR));
            }
        }
        
        return screen;
    }
}

/**
 * Represents a movie show.
 */
class Show {
    private final String id;
    private final Movie movie;
    private final Screen screen;
    private final Date startTime;
    private final Map<String, ShowSeat> showSeats;
    
    public Show(String id, Movie movie, Screen screen, Date startTime) {
        this.id = id;
        this.movie = movie;
        this.screen = screen;
        this.startTime = startTime;
        this.showSeats = new HashMap<>();
        
        // Initialize show seats from screen seats
        for (Seat seat : screen.getSeats()) {
            showSeats.put(seat.getId(), new ShowSeat(seat, seat.getType().getBasePrice()));
        }
    }
    
    public String getId() { return id; }
    public Movie getMovie() { return movie; }
    public Screen getScreen() { return screen; }
    public Date getStartTime() { return startTime; }
    
    public ShowSeat getShowSeat(String seatId) {
        return showSeats.get(seatId);
    }
    
    public List<ShowSeat> getAvailableSeats() {
        List<ShowSeat> available = new ArrayList<>();
        for (ShowSeat showSeat : showSeats.values()) {
            if (showSeat.isAvailable()) {
                available.add(showSeat);
            }
        }
        return available;
    }
    
    public boolean lockSeats(List<String> seatIds, String userId) {
        // First check all seats are available
        for (String seatId : seatIds) {
            ShowSeat showSeat = showSeats.get(seatId);
            if (showSeat == null || !showSeat.isAvailable()) {
                return false;
            }
        }
        
        // Lock all seats
        for (String seatId : seatIds) {
            showSeats.get(seatId).lock(userId);
        }
        
        return true;
    }
    
    public void unlockSeats(List<String> seatIds) {
        for (String seatId : seatIds) {
            ShowSeat showSeat = showSeats.get(seatId);
            if (showSeat != null) {
                showSeat.unlock();
            }
        }
    }
    
    public boolean bookSeats(List<String> seatIds, String userId) {
        for (String seatId : seatIds) {
            ShowSeat showSeat = showSeats.get(seatId);
            if (showSeat == null || !showSeat.book(userId)) {
                return false;
            }
        }
        return true;
    }
    
    public void displaySeats() {
        System.out.println("\n=== Seat Map for " + movie.getTitle() + " ===");
        Map<String, List<ShowSeat>> byRow = new TreeMap<>();
        
        for (ShowSeat showSeat : showSeats.values()) {
            byRow.computeIfAbsent(showSeat.getSeat().getRow(), k -> new ArrayList<>())
                 .add(showSeat);
        }
        
        for (Map.Entry<String, List<ShowSeat>> entry : byRow.entrySet()) {
            List<ShowSeat> rowSeats = entry.getValue();
            rowSeats.sort((a, b) -> a.getSeat().getNumber() - b.getSeat().getNumber());
            
            StringBuilder sb = new StringBuilder(entry.getKey() + ": ");
            for (ShowSeat seat : rowSeats) {
                sb.append(seat).append(" ");
            }
            sb.append("(").append(rowSeats.get(0).getSeat().getType()).append(")");
            System.out.println(sb);
        }
        System.out.println("Legend: [ ] = Available, [L] = Locked, [X] = Booked");
    }
    
    @Override
    public String toString() {
        return movie.getTitle() + " at " + screen.getName() + " - " + startTime;
    }
}

/**
 * Represents a booking.
 */
class Booking {
    private final String id;
    private final Show show;
    private final String userId;
    private final List<ShowSeat> seats;
    private BookingStatus status;
    private double totalAmount;
    private final Date createdAt;
    
    public Booking(String id, Show show, String userId, List<ShowSeat> seats) {
        this.id = id;
        this.show = show;
        this.userId = userId;
        this.seats = new ArrayList<>(seats);
        this.status = BookingStatus.PENDING;
        this.totalAmount = seats.stream().mapToDouble(ShowSeat::getPrice).sum();
        this.createdAt = new Date();
    }
    
    public String getId() { return id; }
    public Show getShow() { return show; }
    public String getUserId() { return userId; }
    public List<ShowSeat> getSeats() { return seats; }
    public BookingStatus getStatus() { return status; }
    public double getTotalAmount() { return totalAmount; }
    public Date getCreatedAt() { return createdAt; }
    
    public void confirm() {
        this.status = BookingStatus.CONFIRMED;
    }
    
    public void cancel() {
        this.status = BookingStatus.CANCELLED;
        // Unlock seats
        for (ShowSeat seat : seats) {
            seat.unlock();
        }
    }
    
    @Override
    public String toString() {
        StringBuilder sb = new StringBuilder();
        sb.append("Booking #").append(id).append("\n");
        sb.append("Movie: ").append(show.getMovie().getTitle()).append("\n");
        sb.append("Show: ").append(show.getStartTime()).append("\n");
        sb.append("Seats: ");
        for (ShowSeat seat : seats) {
            sb.append(seat.getSeat()).append(" ");
        }
        sb.append("\n");
        sb.append("Total: $").append(String.format("%.2f", totalAmount)).append("\n");
        sb.append("Status: ").append(status);
        return sb.toString();
    }
}
