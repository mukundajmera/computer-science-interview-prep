package models;

import enums.RoomType;
import enums.RoomStatus;
import java.util.HashSet;
import java.util.Set;

/**
 * Room.java - Hotel room entity.
 */
public class Room {
    private final String roomNumber;
    private final RoomType roomType;
    private final int floor;
    private double basePrice;
    private RoomStatus status;
    private final Set<String> amenities;

    public Room(String roomNumber, RoomType roomType, int floor) {
        this.roomNumber = roomNumber;
        this.roomType = roomType;
        this.floor = floor;
        this.basePrice = roomType.getBasePrice();
        this.status = RoomStatus.AVAILABLE;
        this.amenities = new HashSet<>();
    }

    public String getRoomNumber() {
        return roomNumber;
    }

    public RoomType getRoomType() {
        return roomType;
    }

    public int getFloor() {
        return floor;
    }

    public double getBasePrice() {
        return basePrice;
    }

    public RoomStatus getStatus() {
        return status;
    }

    public int getMaxOccupancy() {
        return roomType.getMaxOccupancy();
    }

    public void setBasePrice(double price) {
        this.basePrice = price;
    }

    public void setStatus(RoomStatus status) {
        this.status = status;
    }

    public void addAmenity(String amenity) {
        amenities.add(amenity);
    }

    public Set<String> getAmenities() {
        return new HashSet<>(amenities);
    }

    @Override
    public String toString() {
        return String.format("Room[%s, %s, Floor %d, $%.2f/night]",
                roomNumber, roomType, floor, basePrice);
    }
}
