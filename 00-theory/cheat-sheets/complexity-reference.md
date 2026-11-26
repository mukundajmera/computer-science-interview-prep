# Time & Space Complexity Reference

## Data Structures

| Structure | Access | Search | Insert | Delete | Space |
|-----------|--------|--------|--------|--------|-------|
| Array | O(1) | O(n) | O(n) | O(n) | O(n) |
| LinkedList | O(n) | O(n) | O(1) | O(1) | O(n) |
| HashMap | O(1)* | O(1)* | O(1)* | O(1)* | O(n) |
| TreeMap | O(log n) | O(log n) | O(log n) | O(log n) | O(n) |
| HashSet | - | O(1)* | O(1)* | O(1)* | O(n) |
| TreeSet | - | O(log n) | O(log n) | O(log n) | O(n) |
| Heap | O(1) top | O(n) | O(log n) | O(log n) | O(n) |
| Queue | O(1) | O(n) | O(1) | O(1) | O(n) |
| Stack | O(1) | O(n) | O(1) | O(1) | O(n) |

*amortized

---

## LLD Operation Complexities

### Parking Lot
| Operation | Time | Space |
|-----------|------|-------|
| parkVehicle | O(F) | O(1) |
| unparkVehicle | O(1) | O(1) |
| findVehicle | O(1) | O(1) |
| getAvailableSpots | O(F) | O(1) |

F = floors

### Elevator System
| Operation | Time | Space |
|-----------|------|-------|
| addDestination | O(log D) | O(1) |
| selectElevator | O(E) | O(1) |
| step | O(E log D) | O(1) |

E = elevators, D = destinations

### LRU Cache
| Operation | Time | Space |
|-----------|------|-------|
| get | O(1) | O(1) |
| put | O(1) | O(1) |
| Total | - | O(capacity) |

### Rate Limiter
| Algorithm | Time | Space |
|-----------|------|-------|
| Token Bucket | O(1) | O(1) |
| Fixed Window | O(1) | O(1) |
| Sliding Log | O(n) | O(n) |
| Sliding Counter | O(1) | O(1) |

---

## Algorithm Complexities

| Algorithm | Time | Space |
|-----------|------|-------|
| Binary Search | O(log n) | O(1) |
| BFS/DFS | O(V + E) | O(V) |
| Dijkstra | O(E log V) | O(V) |
| Merge Sort | O(n log n) | O(n) |
| Quick Sort | O(n log n)* | O(log n) |

---

## Interview Quick Answers

**"What's the complexity?"**
- HashMap operations: **O(1)** amortized
- TreeSet/TreeMap: **O(log n)**
- Finding in unsorted: **O(n)**
- Sorting comparison: **O(n log n)** minimum

**"Why this data structure?"**
- Fast lookup → HashMap
- Sorted order → TreeSet/TreeMap
- FIFO → Queue
- LIFO → Stack
- Min/Max access → Heap
