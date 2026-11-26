import java.util.ArrayList;
import java.util.Date;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.TreeMap;

/**
 * Movie Ticket Booking System entities.
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

class Movie {
    private final String id;
    private final String title;
    private final int durationMinutes;
    private final String genre;
    private final String rating;

    public Movie(String id, String title, int durationMinutes, String genre) {
        this(id, title, durationMinutes, genre, null);
    }

    public Movie(String id, String title, int durationMinutes, String genre, String rating) {
        this.id = id;
        this.title = title;
        this.durationMinutes = durationMinutes;
        this.genre = genre;
        this.rating = rating;
    }

    public String getId() { return id; }
    public String getTitle() { return title; }
    public int getDurationMinutes() { return durationMinutes; }
    public String getGenre() { return genre; }
    public String getRating() { return rating; }

    @Override
    public String toString() {
        String ratingPart = rating == null ? "" : ", " + rating;
        return title + " (" + genre + ratingPart + ", " + durationMinutes + " min)";
    }
}

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

class ShowSeat {
    private static long lockTimeoutMs = 10L * 60L * 1000L;

    private final Seat seat;
    private final double price;
    private SeatStatus status;
    private String lockedBy;
    private long lockedAt;

    public ShowSeat(Seat seat, double price) {
        this.seat = seat;
        this.price = price;
        this.status = SeatStatus.AVAILABLE;
        this.lockedBy = null;
        this.lockedAt = 0L;
    }

    public static synchronized void setLockTimeoutMs(long timeoutMs) {
        lockTimeoutMs = Math.max(1L, timeoutMs);
    }

    public static synchronized long getLockTimeoutMs() {
        return lockTimeoutMs;
    }

    public synchronized Seat getSeat() { return seat; }
    public synchronized SeatStatus getStatus() { return status; }
    public synchronized double getPrice() { return price; }
    public synchronized String getLockedBy() { return lockedBy; }

    public synchronized boolean isAvailable() {
        if (status == SeatStatus.LOCKED && isLockExpired()) {
            unlock();
        }
        return status == SeatStatus.AVAILABLE;
    }

    private synchronized boolean isLockExpired() {
        return status == SeatStatus.LOCKED && (System.currentTimeMillis() - lockedAt) > lockTimeoutMs;
    }

    public synchronized boolean isLockedBy(String userId) {
        return status == SeatStatus.LOCKED && lockedBy != null && lockedBy.equals(userId);
    }

    public synchronized boolean lock(String userId) {
        if (userId == null || userId.trim().isEmpty()) {
            return false;
        }
        if (!isAvailable()) {
            return false;
        }
        status = SeatStatus.LOCKED;
        lockedBy = userId;
        lockedAt = System.currentTimeMillis();
        return true;
    }

    public synchronized void unlock() {
        status = SeatStatus.AVAILABLE;
        lockedBy = null;
        lockedAt = 0L;
    }

    public synchronized boolean unlockIfOwnedBy(String userId) {
        if (isLockedBy(userId)) {
            unlock();
            return true;
        }
        return false;
    }

    public synchronized boolean book(String userId) {
        if (!isLockedBy(userId)) {
            return false;
        }
        status = SeatStatus.BOOKED;
        return true;
    }

    @Override
    public synchronized String toString() {
        String statusMark;
        switch (status) {
            case AVAILABLE:
                statusMark = "[ ]";
                break;
            case LOCKED:
                statusMark = "[L]";
                break;
            case BOOKED:
                statusMark = "[X]";
                break;
            default:
                statusMark = "[?]";
                break;
        }
        return seat.toString() + statusMark;
    }
}

class Screen {
    private final String id;
    private final String name;
    private final List<Seat> seats;

    public Screen(String id, String name) {
        this.id = id;
        this.name = name;
        this.seats = new ArrayList<Seat>();
    }

    public void addSeat(Seat seat) {
        seats.add(seat);
    }

    public String getId() { return id; }
    public String getName() { return name; }
    public List<Seat> getSeats() { return new ArrayList<Seat>(seats); }
    public int getCapacity() { return seats.size(); }

    public static Screen createStandardScreen(
        String id,
        String name,
        int vipRows,
        int premiumRows,
        int regularRows,
        int seatsPerRow
    ) {
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
        this.showSeats = new HashMap<String, ShowSeat>();

        for (Seat seat : screen.getSeats()) {
            showSeats.put(seat.getId(), new ShowSeat(seat, seat.getType().getBasePrice()));
        }
    }

    public String getId() { return id; }
    public Movie getMovie() { return movie; }
    public Screen getScreen() { return screen; }
    public Date getStartTime() { return startTime; }

    public synchronized ShowSeat getShowSeat(String seatId) {
        return showSeats.get(seatId);
    }

    public synchronized List<ShowSeat> getAvailableSeats() {
        List<ShowSeat> available = new ArrayList<ShowSeat>();
        for (ShowSeat showSeat : showSeats.values()) {
            if (showSeat.isAvailable()) {
                available.add(showSeat);
            }
        }
        return available;
    }

    public synchronized boolean areSeatsLockedByUser(List<String> seatIds, String userId) {
        if (seatIds == null || seatIds.isEmpty() || userId == null) {
            return false;
        }
        for (String seatId : seatIds) {
            ShowSeat showSeat = showSeats.get(seatId);
            if (showSeat == null || !showSeat.isLockedBy(userId)) {
                return false;
            }
        }
        return true;
    }

    public synchronized boolean lockSeats(List<String> seatIds, String userId) {
        if (seatIds == null || seatIds.isEmpty() || userId == null || userId.trim().isEmpty()) {
            return false;
        }

        for (String seatId : seatIds) {
            ShowSeat showSeat = showSeats.get(seatId);
            if (showSeat == null || !showSeat.isAvailable()) {
                return false;
            }
        }

        List<ShowSeat> lockedSeats = new ArrayList<ShowSeat>();
        for (String seatId : seatIds) {
            ShowSeat showSeat = showSeats.get(seatId);
            if (!showSeat.lock(userId)) {
                for (ShowSeat locked : lockedSeats) {
                    locked.unlockIfOwnedBy(userId);
                }
                return false;
            }
            lockedSeats.add(showSeat);
        }

        return true;
    }

    public synchronized void unlockSeats(List<String> seatIds) {
        if (seatIds == null) {
            return;
        }
        for (String seatId : seatIds) {
            ShowSeat showSeat = showSeats.get(seatId);
            if (showSeat != null) {
                showSeat.unlock();
            }
        }
    }

    public synchronized boolean bookSeats(List<String> seatIds, String userId) {
        if (seatIds == null || seatIds.isEmpty() || userId == null) {
            return false;
        }

        for (String seatId : seatIds) {
            ShowSeat showSeat = showSeats.get(seatId);
            if (showSeat == null || !showSeat.isLockedBy(userId)) {
                return false;
            }
        }

        for (String seatId : seatIds) {
            ShowSeat showSeat = showSeats.get(seatId);
            if (!showSeat.book(userId)) {
                return false;
            }
        }
        return true;
    }

    public synchronized void displaySeats() {
        System.out.println("\n=== Seat Map for " + movie.getTitle() + " ===");
        Map<String, List<ShowSeat>> byRow = new TreeMap<String, List<ShowSeat>>();

        for (ShowSeat showSeat : showSeats.values()) {
            String row = showSeat.getSeat().getRow();
            if (!byRow.containsKey(row)) {
                byRow.put(row, new ArrayList<ShowSeat>());
            }
            byRow.get(row).add(showSeat);
        }

        for (Map.Entry<String, List<ShowSeat>> entry : byRow.entrySet()) {
            List<ShowSeat> rowSeats = entry.getValue();
            rowSeats.sort((a, b) -> Integer.compare(a.getSeat().getNumber(), b.getSeat().getNumber()));

            StringBuilder sb = new StringBuilder(entry.getKey() + ": ");
            for (ShowSeat seat : rowSeats) {
                sb.append(seat).append(" ");
            }
            sb.append("(").append(rowSeats.get(0).getSeat().getType()).append(")");
            System.out.println(sb.toString());
        }
        System.out.println("Legend: [ ] = Available, [L] = Locked, [X] = Booked");
    }

    @Override
    public String toString() {
        return movie.getTitle() + " at " + screen.getName() + " - " + startTime;
    }
}

class Booking {
    private final String id;
    private final Show show;
    private final String userId;
    private final List<ShowSeat> seats;
    private final List<String> seatIds;
    private BookingStatus status;
    private final double totalAmount;
    private final Date createdAt;

    public Booking(String id, Show show, String userId, List<ShowSeat> seats) {
        this.id = id;
        this.show = show;
        this.userId = userId;
        this.seats = new ArrayList<ShowSeat>(seats);
        this.seatIds = new ArrayList<String>();
        for (ShowSeat seat : seats) {
            this.seatIds.add(seat.getSeat().getId());
        }
        this.status = BookingStatus.PENDING;
        this.totalAmount = seats.stream().mapToDouble(ShowSeat::getPrice).sum();
        this.createdAt = new Date();
    }

    public String getId() { return id; }
    public Show getShow() { return show; }
    public String getUserId() { return userId; }
    public List<ShowSeat> getSeats() { return new ArrayList<ShowSeat>(seats); }
    public List<String> getSeatIds() { return new ArrayList<String>(seatIds); }
    public BookingStatus getStatus() { return status; }
    public double getTotalAmount() { return totalAmount; }
    public Date getCreatedAt() { return createdAt; }

    public void confirm() {
        status = BookingStatus.CONFIRMED;
    }

    public void cancel() {
        status = BookingStatus.CANCELLED;
        show.unlockSeats(seatIds);
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
