# Car Rental System

## Problem Statement

Design a car rental system that manages vehicle inventory, handles reservations, calculates pricing, and processes vehicle returns with damage tracking.

---

## Functional Requirements

1. **Vehicle Inventory**: Add/remove vehicles with details (make, model, type, license plate)
2. **Reservations**: Book vehicles for date ranges with confirmation
3. **Availability Check**: Find available vehicles by type and date range
4. **Pricing**: Calculate rental cost (hourly/daily/weekly rates)
5. **Return Processing**: Process vehicle returns with mileage and condition
6. **Damage Tracking**: Record and track vehicle damage reports
7. **Payment Processing**: Handle payments and refunds
8. **Customer Management**: Track customer history and loyalty

---

## Non-Functional Requirements

1. **Scalability**: Handle multiple locations and large fleet
2. **Concurrency**: Prevent double-booking of same vehicle
3. **Availability**: High uptime for booking operations
4. **Data Integrity**: Accurate reservation and payment records
5. **Performance**: Fast availability searches

---

## Constraints & Assumptions

- Vehicles can only have one active reservation at a time
- Reservations can be cancelled before pickup
- Late returns incur penalty charges
- Fuel policy: Return with same fuel level
- Insurance options available at booking
- Different vehicle types have different pricing

---

## Reservation States

```
Pending → Confirmed → Active → Completed
    ↓
Cancelled
```

---

## Sample Interactions

```
1. Customer searches for SUV available Dec 20-25
2. System shows available SUVs with pricing
3. Customer selects vehicle and books with insurance
4. System confirms reservation and holds vehicle
5. Customer picks up vehicle on Dec 20
6. Customer returns vehicle on Dec 25
7. System calculates final bill (including any damage)
8. Customer pays and receives receipt
```

---

## Entities to Identify

| Entity | Responsibility |
|--------|---------------|
| Vehicle | Vehicle details, availability status |
| Customer | Profile, reservations, payment history |
| Reservation | Booking details, state management |
| Pricing | Calculate rental costs |
| DamageReport | Track vehicle damage |
| Payment | Process transactions |
| RentalService | Main facade for operations |

---

## Version Roadmap

| Version | Features |
|---------|----------|
| v1-basic | Vehicles, customers, reservations, basic pricing |
| v2-extended | Multiple vehicle types, insurance, damage tracking |
| v3-optimized | Concurrent bookings, inventory locking, surge pricing |
