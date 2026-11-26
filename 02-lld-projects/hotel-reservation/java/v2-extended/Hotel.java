import enums.RoomType;
import enums.RoomStatus;
import models.Guest;
import models.Room;
import models.Reservation;
import java.time.LocalDate;
import java.util.*;

/**
 * Hotel.java - Singleton hotel management system.
 * 
 * DESIGN PATTERN: Singleton
 */
public class Hotel {
    private static Hotel instance;
    private final String name;
    private final Map<String, Room> rooms;
    private final Map<String, Reservation> reservations;
    private final Map<String, Guest> guests;

    private Hotel(String name) {
        this.name = name;
        this.rooms = new HashMap<>();
        this.reservations = new HashMap<>();
        this.guests = new HashMap<>();
    }

    public static synchronized Hotel getInstance(String name) {
        if (instance == null) {
            instance = new Hotel(name);
        }
        return instance;
    }

    public void addRoom(Room room) {
        rooms.put(room.getRoomNumber(), room);
    }

    public void registerGuest(Guest guest) {
        guests.put(guest.getGuestId(), guest);
    }

    public List<Room> searchAvailableRooms(LocalDate checkIn, LocalDate checkOut, RoomType type) {
        List<Room> available = new ArrayList<>();
        for (Room room : rooms.values()) {
            if (room.getStatus() == RoomStatus.AVAILABLE) {
                if (type == null || room.getRoomType() == type) {
                    if (isRoomAvailable(room, checkIn, checkOut)) {
                        available.add(room);
                    }
                }
            }
        }
        return available;
    }

    private boolean isRoomAvailable(Room room, LocalDate checkIn, LocalDate checkOut) {
        for (Reservation res : reservations.values()) {
            if (res.getRoom().equals(room)) {
                if (!checkOut.isBefore(res.getCheckInDate()) &&
                        !checkIn.isAfter(res.getCheckOutDate())) {
                    return false;
                }
            }
        }
        return true;
    }

    public Reservation makeReservation(Guest guest, Room room, LocalDate checkIn, LocalDate checkOut) {
        if (!isRoomAvailable(room, checkIn, checkOut)) {
            System.out.println("Room not available for selected dates");
            return null;
        }

        Reservation reservation = new Reservation(guest, room, checkIn, checkOut);
        reservations.put(reservation.getReservationId(), reservation);
        guest.addReservation(reservation);
        System.out.println("Reservation created: " + reservation);
        return reservation;
    }

    public void checkIn(String reservationId) {
        Reservation res = reservations.get(reservationId);
        if (res != null) {
            res.checkIn();
            res.getRoom().setStatus(RoomStatus.OCCUPIED);
            System.out.println("Checked in: " + res.getGuest().getName());
        }
    }

    public void checkOut(String reservationId) {
        Reservation res = reservations.get(reservationId);
        if (res != null) {
            res.checkOut();
            res.getRoom().setStatus(RoomStatus.CLEANING);
            System.out.println("Checked out: " + res.getGuest().getName() +
                    " - Total: $" + res.getTotalAmount());
        }
    }

    public String getName() {
        return name;
    }
}
