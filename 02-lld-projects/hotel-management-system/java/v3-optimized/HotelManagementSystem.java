
import java.util.*;
import java.time.LocalDateTime;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.locks.ReentrantLock;

enum HousekeepingStatus {
    CLEAN, DIRTY, INSPECTED
}

enum RoomType {
    STANDARD, DELUXE, SUITE
}

class Charge {
    private String description;
    private double amount;
    private LocalDateTime timestamp;

    public Charge(String description, double amount) {
        this.description = description;
        this.amount = amount;
        this.timestamp = LocalDateTime.now();
    }

    public double getAmount() {
        return amount;
    }
}

class RoomKey {
    private String keyId;
    private String roomId;
    private boolean isActive;

    public RoomKey(String roomId) {
        this.keyId = UUID.randomUUID().toString();
        this.roomId = roomId;
        this.isActive = true;
    }

    public void deactivate() {
        this.isActive = false;
    }

    public boolean isActive() {
        return isActive;
    }
}

class Folio {
    private String stayId;
    private List<Charge> charges;
    private double balance;
    private final ReentrantLock lock = new ReentrantLock();

    public Folio(String stayId) {
        this.stayId = stayId;
        this.charges = new ArrayList<>();
        this.balance = 0.0;
    }

    public void addCharge(Charge charge) {
        lock.lock();
        try {
            charges.add(charge);
            balance += charge.getAmount();
        } finally {
            lock.unlock();
        }
    }

    public void processPayment(double amount) {
        lock.lock();
        try {
            if (amount <= balance) {
                balance -= amount;
            } else {
                throw new IllegalArgumentException("Overpayment not allowed");
            }
        } finally {
            lock.unlock();
        }
    }

    public double getBalance() {
        lock.lock();
        try {
            return balance;
        } finally {
            lock.unlock();
        }
    }
    
    public ReentrantLock getLock() {
        return lock;
    }
}

class Room {
    private String roomId;
    private RoomType roomType;
    private HousekeepingStatus status;
    private boolean isOccupied;
    private final ReentrantLock lock = new ReentrantLock();

    public Room(String roomId, RoomType roomType) {
        this.roomId = roomId;
        this.roomType = roomType;
        this.status = HousekeepingStatus.CLEAN;
        this.isOccupied = false;
    }

    public String getRoomId() { return roomId; }
    public RoomType getRoomType() { return roomType; }
    
    public HousekeepingStatus getStatus() { 
        lock.lock();
        try {
            return status; 
        } finally {
            lock.unlock();
        }
    }
    
    public void setStatus(HousekeepingStatus status) { 
        lock.lock();
        try {
            this.status = status; 
        } finally {
            lock.unlock();
        }
    }
    
    public boolean isOccupied() { 
        lock.lock();
        try {
            return isOccupied; 
        } finally {
            lock.unlock();
        }
    }
    
    public void setOccupied(boolean occupied) { 
        lock.lock();
        try {
            this.isOccupied = occupied; 
        } finally {
            lock.unlock();
        }
    }
    
    public ReentrantLock getLock() {
        return lock;
    }
}

class Stay {
    private String stayId;
    private String guestName;
    private Room room;
    private Folio folio;
    private List<RoomKey> keys;
    private final ReentrantLock lock = new ReentrantLock();

    public Stay(String guestName, Room room) {
        this.stayId = UUID.randomUUID().toString();
        this.guestName = guestName;
        this.room = room;
        this.folio = new Folio(this.stayId);
        this.keys = new ArrayList<>();
    }

    public RoomKey issueKey() {
        lock.lock();
        try {
            RoomKey key = new RoomKey(room.getRoomId());
            keys.add(key);
            return key;
        } finally {
            lock.unlock();
        }
    }

    public void deactivateKeys() {
        lock.lock();
        try {
            for (RoomKey key : keys) {
                key.deactivate();
            }
        } finally {
            lock.unlock();
        }
    }

    public Room getRoom() { return room; }
    public Folio getFolio() { return folio; }
    
    public List<RoomKey> getKeys() { 
        lock.lock();
        try {
            return new ArrayList<>(keys); 
        } finally {
            lock.unlock();
        }
    }
    public String getGuestName() { return guestName; }
}

class HotelManager {
    private Map<String, Room> rooms = new ConcurrentHashMap<>();
    private Map<String, Stay> activeStays = new ConcurrentHashMap<>();

    public void addRoom(Room room) {
        rooms.put(room.getRoomId(), room);
    }

    public void updateHousekeepingStatus(String roomId, HousekeepingStatus status) {
        Room room = rooms.get(roomId);
        if (room != null) {
            room.setStatus(status);
        }
    }

    public Stay checkIn(String reservationId, String guestName, RoomType roomType) {
        for (Room room : rooms.values()) {
            room.getLock().lock();
            try {
                if (room.getRoomType() == roomType && !room.isOccupied() && room.getStatus() == HousekeepingStatus.INSPECTED) {
                    room.setOccupied(true);
                    Stay stay = new Stay(guestName, room);
                    activeStays.put(room.getRoomId(), stay);
                    return stay;
                }
            } finally {
                room.getLock().unlock();
            }
        }
        return null;
    }

    public void postCharge(String roomId, String description, double amount) {
        Stay stay = activeStays.get(roomId);
        if (stay != null) {
            stay.getFolio().addCharge(new Charge(description, amount));
        } else {
            throw new IllegalStateException("Room is not occupied");
        }
    }

    public void settleFolio(String roomId, double amount) {
        Stay stay = activeStays.get(roomId);
        if (stay != null) {
            stay.getFolio().processPayment(amount);
        }
    }

    public void checkOut(String roomId) {
        Stay stay = activeStays.get(roomId);
        if (stay != null) {
            stay.getFolio().getLock().lock();
            try {
                if (stay.getFolio().getBalance() > 0) {
                    throw new IllegalStateException("Folio must be settled before check-out");
                }
                
                stay.deactivateKeys();
                stay.getRoom().getLock().lock();
                try {
                    stay.getRoom().setOccupied(false);
                    stay.getRoom().setStatus(HousekeepingStatus.DIRTY);
                } finally {
                    stay.getRoom().getLock().unlock();
                }
                activeStays.remove(roomId);
            } finally {
                stay.getFolio().getLock().unlock();
            }
        }
    }
}
