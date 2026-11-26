# Design Approach for Car Rental System

## Step 1: Identify Core Entities

From the problem statement, extract the nouns:

| Noun | Class? | Reason |
|------|--------|--------|
| Vehicle | ✅ | Core entity to rent |
| Customer | ✅ | Who rents vehicles |
| Reservation | ✅ | Booking record |
| Pricing | ✅ | Cost calculation |
| DamageReport | ✅ | Track damages |
| Payment | ✅ | Transaction record |
| Location | ✅ | Pickup/dropoff points |

## Step 2: Define Relationships

```
Customer 1 ----* Reservation
Reservation *----1 Vehicle
Vehicle 1----* DamageReport
Reservation 1----1 Payment
Location 1----* Vehicle
```

## Step 3: Choose Design Patterns

| Pattern | Application |
|---------|-------------|
| **Factory** | Create different vehicle types (Car, SUV, Truck) |
| **Strategy** | Different pricing strategies (hourly, daily, weekly) |
| **State** | Reservation state transitions |
| **Observer** | Notify customers of status changes |
| **Singleton** | Rental service instance |

## Step 4: Design Classes

### Vehicle
- **Attributes**: vehicleId, licensePlate, make, model, type, status, location
- **Methods**: isAvailable(), updateStatus(), calculateMileage()
- **Patterns**: Factory for creating different types

### Customer
- **Attributes**: customerId, name, email, drivingLicense, reservations
- **Methods**: addReservation(), getActiveReservations()

### Reservation
- **Attributes**: reservationId, customer, vehicle, startDate, endDate, status, insurance
- **Methods**: confirm(), cancel(), pickup(), complete()
- **Patterns**: State pattern for status transitions

### PricingStrategy
- **Interface**: calculatePrice(vehicle, duration)
- **Implementations**: HourlyPricing, DailyPricing, WeeklyPricing

### DamageReport
- **Attributes**: reportId, vehicle, description, severity, repairCost, date
- **Methods**: estimateRepairCost()

### Payment
- **Attributes**: paymentId, reservation, amount, status, method
- **Methods**: process(), refund()

## Step 5: Handle Edge Cases

1. **Double Booking**: Lock vehicle during booking process
2. **Cancelled Reservation**: Release vehicle, process refund if applicable
3. **Late Return**: Calculate penalty charges
4. **Damaged Vehicle**: Record damage, add charges
5. **No Available Vehicles**: Suggest alternatives or waitlist
6. **Concurrent Requests**: Use synchronization for availability check

## Step 6: Optimization Opportunities

1. **Availability Index**: HashMap by date range for O(1) lookups
2. **Caching**: Cache popular vehicle searches
3. **Concurrent Locks**: Lock per vehicle, not global
4. **Pricing Precomputation**: Pre-calculate common durations
5. **Surge Pricing**: Adjust based on demand/availability
