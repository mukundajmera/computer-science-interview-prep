# 🏗️ LLD Projects Flashcards

> **40 flashcard questions for Low-Level Design project interviews**

---

### Card 1
**Front:** In a Parking Lot LLD, what design pattern is typically used to ensure only one instance of the parking lot exists?

---

### Card 2
**Front:** How would you model the relationship between a `ParkingTicket` and a `ParkingSpot` in a Parking Lot system?

---

### Card 3
**Front:** In a Parking Lot design, which class is responsible for finding the next available parking spot?

---

### Card 4
**Front:** How does the Strategy pattern apply to calculating parking fees in a Parking Lot LLD?

---

### Card 5
**Front:** Which design pattern is best suited for handling the different phases (e.g., Idle, HasMoney, Dispensing) of a Vending Machine?

---

### Card 6
**Front:** In a Vending Machine LLD, what exception should be thrown if a user attempts to select a product before inserting money?

---

### Card 7
**Front:** How do you ensure thread safety when multiple users attempt to purchase the last remaining item in a Vending Machine concurrently?

---

### Card 8
**Front:** What is the role of an `Inventory` class in the Vending Machine system design?

---

### Card 9
**Front:** In a Library Management system, what is the difference between a `Book` and a `BookItem`?

---

### Card 10
**Front:** How would you model the relationship between a `Member` and a `LibraryCard`?

---

### Card 11
**Front:** Which design pattern can be used to notify members when a reserved book becomes available in the library?

---

### Card 12
**Front:** How do you handle the state transition of a `BookItem` when it is checked out, returned, or lost?

---

### Card 13
**Front:** In an LRU Cache LLD, what combination of data structures is used to achieve O(1) time complexity for `get` and `put` operations?

---

### Card 14
**Front:** Why is a Doubly Linked List preferred over a Singly Linked List in the implementation of an LRU Cache?

---

### Card 15
**Front:** In an LRU Cache design, what happens when the cache reaches its maximum capacity and a new item is added?

---

### Card 16
**Front:** How would you make an LRU Cache thread-safe in a multi-threaded environment?

---

### Card 17
**Front:** In a Message Queue LLD, what is the difference between the Point-to-Point and Publisher-Subscriber messaging models?

---

### Card 18
**Front:** How do you implement the 'at-least-once' delivery semantic in a custom Message Queue design?

---

### Card 19
**Front:** What is the role of a `Topic` and a `Subscription` in a Pub/Sub Message Queue?

---

### Card 20
**Front:** How would you handle message ordering guarantees within a specific partition of a Message Queue?

---

### Card 21
**Front:** In a Movie Ticket Booking system, how do you handle concurrency when two users try to book the same seat simultaneously?

---

### Card 22
**Front:** What is the difference between a `Show` and a `Movie` in the context of a Ticket Booking LLD?

---

### Card 23
**Front:** How does the system automatically release a reserved seat if the payment is not completed within a given time limit?

---

### Card 24
**Front:** Which design pattern can be used to apply different pricing strategies (e.g., weekend vs weekday) for movie tickets?

---

### Card 25
**Front:** In an Elevator System LLD, which component is responsible for dispatching an elevator to a requested floor?

---

### Card 26
**Front:** What algorithmic approach (e.g., SCAN, LOOK) is commonly used to optimize elevator movement and reduce passenger wait times?

---

### Card 27
**Front:** How do you model internal and external elevator buttons differently in an Elevator System?

---

### Card 28
**Front:** What design pattern is useful for representing the states of an elevator, such as MovingUp, MovingDown, and Idle?

---

### Card 29
**Front:** In a Tic-Tac-Toe LLD, what data structure is most appropriate for representing the game board?

---

### Card 30
**Front:** How can you optimize the check for a winning condition to O(1) instead of traversing the board every time?

---

### Card 31
**Front:** In a Tic-Tac-Toe design, how would you model a generic `Player` to support both Human and Bot opponents?

---

### Card 32
**Front:** What is the role of a `GameController` or `Game` class in managing the turn-based flow of a Tic-Tac-Toe match?

---

### Card 33
**Front:** In a Rate Limiter LLD, how does the Token Bucket algorithm differ from the Leaky Bucket algorithm?

---

### Card 34
**Front:** What is the primary advantage of using a Sliding Window Log over a Fixed Window Counter in a Rate Limiter design?

---

### Card 35
**Front:** How do you store and retrieve the request counts per user efficiently in a distributed Rate Limiter?

---

### Card 36
**Front:** Which design pattern can be used to chain different rate-limiting rules (e.g., per-IP, per-user) together?

---

### Card 37
**Front:** In an Amazon Locker LLD, what state transitions occur from package deposit to pickup for a valid token?

---

### Card 38
**Front:** Why should the locker allocation logic in an Amazon Locker system be extracted into a policy abstraction (Strategy pattern)?

---

### Card 39
**Front:** What boundary conditions should be tested for `clearExpiredDeposits()` without using `sleep`?

---

### Card 40
**Front:** How does an injectable clock improve the testing of reservation and token TTLs in an Amazon Locker design?

---

<p align="center">
  <b>Total: 40 Flashcards</b>
</p>
