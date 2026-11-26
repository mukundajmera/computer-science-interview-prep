# Design Approach for Parking Lot System

A step-by-step thought process for designing the parking lot system.

---

## Step 1: Identify Core Entities

Extract nouns from the problem statement:

| Noun | Entity? | Reasoning |
|------|---------|-----------|
| Parking Lot | ✅ Yes | Main system container |
| Floor | ✅ Yes | Logical grouping of spots |
| Parking Spot | ✅ Yes | Where vehicles park |
| Vehicle | ✅ Yes | What gets parked |
| Ticket | ✅ Yes | Entry/exit record |
| Fee/Rate | ✅ Yes | Pricing logic |
| Barrier/Gate | ❌ No | Hardware, out of scope |

**Final Entities**: ParkingLot, Floor, ParkingSpot, Vehicle, Ticket, ParkingRate

---

## Step 2: Define Relationships

```
ParkingLot (1) ──contains──> (n) Floor
Floor (1) ──contains──> (n) ParkingSpot  
ParkingSpot (1) ──holds──> (0..1) Vehicle
ParkingLot (1) ──issues──> (n) Ticket
Ticket (1) ──references──> (1) ParkingSpot
Ticket (1) ──references──> (1) Vehicle
```

### Relationship Types:

| Relationship | Type | Description |
|--------------|------|-------------|
| ParkingLot → Floor | Composition | Floors don't exist without lot |
| Floor → ParkingSpot | Composition | Spots belong to floor |
| ParkingSpot → Vehicle | Aggregation | Vehicle exists independently |
| Ticket → Vehicle | Association | Reference for lookup |

---

## Step 3: Choose Design Patterns

### Pattern Analysis:

| Pattern | Apply? | Justification |
|---------|--------|---------------|
| **Singleton** | ✅ Yes | One parking lot instance |
| **Factory** | ✅ Yes | Create different vehicle types |
| **Strategy** | ✅ Yes | Different pricing strategies |
| **Observer** | 🔄 v2 | Notifications on spot change |
| **State** | ❌ No | Spots are simple occupied/free |

### Pattern Application:

1. **Singleton Pattern** - ParkingLot
   - Ensures single point of control
   - Global access for vehicle operations

2. **Factory Pattern** - VehicleFactory
   - Creates Car, Motorcycle, Truck instances
   - Encapsulates vehicle creation logic

3. **Strategy Pattern** - PricingStrategy
   - HourlyPricing, DailyPricing, WeekendPricing
   - Easily swap pricing algorithms

---

## Step 4: Design Classes

### Core Classes:

#### ParkingLot (Singleton)
- **Attributes**: 
  - `floors: List<Floor>`
  - `activeTickets: Map<String, Ticket>`
  - `pricingStrategy: PricingStrategy`
- **Methods**:
  - `parkVehicle(vehicle): Ticket`
  - `unparkVehicle(ticket): Payment`
  - `getAvailableSpots(vehicleType): int`
  - `findVehicle(licensePlate): ParkingSpot`

#### Floor
- **Attributes**:
  - `floorNumber: int`
  - `spots: List<ParkingSpot>`
  - `availableSpotsByType: Map<VehicleType, int>`
- **Methods**:
  - `parkVehicle(vehicle): ParkingSpot`
  - `unparkVehicle(spot): void`
  - `getAvailableSpots(type): int`

#### ParkingSpot
- **Attributes**:
  - `spotId: String`
  - `spotType: SpotType`
  - `floor: Floor`
  - `vehicle: Vehicle`
  - `isOccupied: boolean`
- **Methods**:
  - `park(vehicle): boolean`
  - `unpark(): Vehicle`
  - `canFit(vehicle): boolean`

#### Vehicle (Abstract)
- **Attributes**:
  - `licensePlate: String`
  - `type: VehicleType`
- **Subclasses**: Car, Motorcycle, Truck

#### Ticket
- **Attributes**:
  - `ticketId: String`
  - `vehicle: Vehicle`
  - `spot: ParkingSpot`
  - `entryTime: DateTime`
  - `exitTime: DateTime`
- **Methods**:
  - `getDuration(): Duration`

#### PricingStrategy (Interface)
- **Methods**:
  - `calculateFee(ticket): double`
- **Implementations**: HourlyPricing, FlatRatePricing

---

## Step 5: Handle Edge Cases

### Input Validation:
- Null vehicle or ticket
- Invalid license plate format
- Empty ticket ID

### Business Logic:
- Parking lot full - no spots available
- Vehicle type too large for available spots
- Exit without valid entry ticket
- Double parking (same vehicle trying to park twice)
- Same spot assigned to multiple vehicles

### Concurrency (v3):
- Multiple vehicles entering simultaneously
- Race condition on last spot
- Ticket lookup during unpark

---

## Step 6: Optimization Opportunities

### Data Structures:
| Operation | Naive | Optimized |
|-----------|-------|-----------|
| Find available spot | O(n) scan | O(1) with free list |
| Lookup by ticket | O(n) search | O(1) with HashMap |
| Lookup by plate | O(n) search | O(1) with HashMap index |

### Caching:
- Cache spot counts per floor/type
- Update counts on park/unpark

### Indexing:
- `Map<VehicleType, Queue<ParkingSpot>>` - Free spots by type
- `Map<String, Ticket>` - Active tickets by ID
- `Map<String, ParkingSpot>` - Vehicle plate to spot

---

## Step 7: Version Progression

### v1-basic
- Core classes with simple implementation
- Linear search for spots
- Basic fee calculation
- Single-threaded

### v2-extended
- Payment processing with multiple methods
- Reserved spot support
- Notification on events
- Better error handling

### v3-optimized
- Thread-safe with locks
- Concurrent spot allocation
- HashMap indexing for O(1) lookups
- Optimized spot allocation queues

---

## Code Organization

```
parking-lot/
├── java/
│   ├── v1-basic/
│   │   ├── ParkingLot.java      # Main system + Singleton
│   │   ├── Vehicle.java         # Abstract + subclasses
│   │   ├── ParkingSpot.java     # Spot with type
│   │   ├── Ticket.java          # Entry record
│   │   └── ParkingDemo.java     # Usage example
│   ├── v2-extended/
│   │   ├── [All v1 classes enhanced]
│   │   ├── Payment.java         # Payment processing
│   │   ├── PricingStrategy.java # Strategy pattern
│   │   └── Reservation.java     # Reserved spots
│   └── v3-optimized/
│       └── [Thread-safe versions]
└── python/
    └── [Same structure]
```

---

## Interview Discussion Points

1. **Why Singleton for ParkingLot?**
   - Ensures centralized control
   - Prevents inconsistent state across instances
   - Trade-off: harder to test, consider dependency injection

2. **Why Strategy for Pricing?**
   - Open for extension (new pricing rules)
   - Closed for modification (existing code unchanged)
   - Easy to swap at runtime

3. **How to scale to multiple lots?**
   - Remove Singleton, use Factory
   - Central management system
   - Distributed spot allocation
