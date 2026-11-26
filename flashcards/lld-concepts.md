# 🏗️ LLD Concepts Flashcards

> **100 flashcard questions for mastering Low-Level Design concepts**

---

## OOP Fundamentals (15 Cards)

### Card 1
**Front:** What are the 4 pillars of Object-Oriented Programming?

---

### Card 2
**Front:** What is the difference between Encapsulation and Abstraction?

---

### Card 3
**Front:** What are the types of Polymorphism? Give examples of each.

---

### Card 4
**Front:** What is the difference between method overloading and method overriding?

---

### Card 5
**Front:** What is the difference between an Abstract Class and an Interface?

---

### Card 6
**Front:** When should you use an abstract class vs an interface?

---

### Card 7
**Front:** What is tight coupling and why is it bad?

---

### Card 8
**Front:** What is high cohesion and why is it good?

---

### Card 9
**Front:** What is the difference between compile-time and runtime polymorphism?

---

### Card 10
**Front:** How does encapsulation protect data integrity?

---

### Card 11
**Front:** What is the diamond problem in multiple inheritance?

---

### Card 12
**Front:** How does Java solve the diamond problem with interfaces?

---

### Card 13
**Front:** What is dynamic method dispatch?

---

### Card 14
**Front:** What is the purpose of access modifiers in OOP?

---

### Card 15
**Front:** What is the difference between association and dependency?

---

---

## SOLID Principles (20 Cards)

### Card 16
**Front:** What is the Single Responsibility Principle (SRP)? Give an example.

---

### Card 17
**Front:** Give an example of SRP violation and how to fix it.

---

### Card 18
**Front:** What is the Open/Closed Principle (OCP)? Provide code example.

---

### Card 19
**Front:** How do you achieve the Open/Closed Principle in practice?

---

### Card 20
**Front:** What is the Liskov Substitution Principle (LSP)?

---

### Card 21
**Front:** Give an example of LSP violation.

---

### Card 22
**Front:** What is the Interface Segregation Principle (ISP)?

---

### Card 23
**Front:** What is the fat interface problem in ISP?

---

### Card 24
**Front:** What is the Dependency Inversion Principle (DIP)?

---

### Card 25
**Front:** Give an example of DIP with dependency injection.

---

### Card 26
**Front:** How does SRP relate to cohesion?

---

### Card 27
**Front:** What are the benefits of following SOLID principles?

---

### Card 28
**Front:** How does OCP reduce the risk of introducing bugs?

---

### Card 29
**Front:** What is the relationship between LSP and polymorphism?

---

### Card 30
**Front:** How does ISP prevent forced implementation?

---

### Card 31
**Front:** What is the difference between DIP and dependency injection?

---

### Card 32
**Front:** How do SOLID principles support unit testing?

---

### Card 33
**Front:** What happens when you violate the Single Responsibility Principle?

---

### Card 34
**Front:** How do you identify if a class has more than one responsibility?

---

### Card 35
**Front:** What is the relationship between OCP and Strategy pattern?

---

---

## Composition vs Inheritance (10 Cards)

### Card 36
**Front:** Why should you favor composition over inheritance?

---

### Card 37
**Front:** When should you use composition vs inheritance?

---

### Card 38
**Front:** What is a HAS-A vs IS-A relationship?

---

### Card 39
**Front:** What is the fragile base class problem?

---

### Card 40
**Front:** How does composition provide more flexibility than inheritance?

---

### Card 41
**Front:** What is the difference between composition and aggregation?

---

### Card 42
**Front:** Give an example where inheritance is more appropriate than composition.

---

### Card 43
**Front:** How does composition support the Open/Closed Principle?

---

### Card 44
**Front:** What is mixin composition?

---

### Card 45
**Front:** How do you refactor from inheritance to composition?

---

---

## Design Principles (10 Cards)

### Card 46
**Front:** What is the DRY principle? Give an example.

---

### Card 47
**Front:** What is the KISS principle?

---

### Card 48
**Front:** What is the YAGNI principle?

---

### Card 49
**Front:** What is the Law of Demeter (LoD)?

---

### Card 50
**Front:** What does "Program to interface, not implementation" mean?

---

### Card 51
**Front:** What is the Principle of Least Astonishment?

---

### Card 52
**Front:** How does separation of concerns apply to software design?

---

### Card 53
**Front:** What is the difference between accidental and essential complexity?

---

### Card 54
**Front:** What is the Hollywood Principle (Don't call us, we'll call you)?

---

### Card 55
**Front:** How do you balance YAGNI with extensibility?

---

---

## Class Relationships (15 Cards)

### Card 56
**Front:** What is the difference between Association, Aggregation, and Composition?

---

### Card 57
**Front:** What are the UML symbols for different class relationships?

---

### Card 58
**Front:** What is the difference between Dependency and Association?

---

### Card 59
**Front:** What is multiplicity in UML and how is it represented?

---

### Card 60
**Front:** What is a unidirectional vs bidirectional association?

---

### Card 61
**Front:** How do you represent inheritance in UML?

---

### Card 62
**Front:** How do you represent interface implementation in UML?

---

### Card 63
**Front:** What is a realization relationship in UML?

---

### Card 64
**Front:** How do you show cardinality in class diagrams?

---

### Card 65
**Front:** What is the difference between whole-part and uses relationships?

---

### Card 66
**Front:** How do you identify association vs composition in requirements?

---

### Card 67
**Front:** What does the arrow direction mean in UML associations?

---

### Card 68
**Front:** How do you represent abstract classes and interfaces in UML?

---

### Card 69
**Front:** What is a stereotype in UML?

---

### Card 70
**Front:** How do you show method visibility in UML class diagrams?

---

---

## Code Smells & Refactoring (10 Cards)

### Card 71
**Front:** What are code smells? Give 5 examples.

---

### Card 72
**Front:** How do you fix the Long Method code smell?

---

### Card 73
**Front:** How do you refactor duplicate code?

---

### Card 74
**Front:** How do you solve the Large Class code smell?

---

### Card 75
**Front:** What is the Feature Envy code smell?

---

### Card 76
**Front:** What is Shotgun Surgery and how do you fix it?

---

### Card 77
**Front:** What is the Data Class code smell?

---

### Card 78
**Front:** What is Primitive Obsession and its solution?

---

### Card 79
**Front:** What is the Switch Statement code smell?

---

### Card 80
**Front:** How do you identify when to apply Extract Method refactoring?

---

## Concurrency & Thread-Safety (12 Cards)

### Card 81
**Front:** How do you detect a check-then-act race in an LLD flow?

---

### Card 82
**Front:** What is a read-modify-write race and why is it unsafe without atomicity?

---

### Card 83
**Front:** When should coarse-grained locking be preferred over fine-grained locking?

---

### Card 84
**Front:** How does deterministic lock ordering reduce deadlock risk?

---

### Card 85
**Front:** What system risk does a bounded blocking queue address under burst traffic?

---

### Card 86
**Front:** Why is busy-wait polling usually a weak coordination strategy?

---

### Card 87
**Front:** When is a semaphore/permit gate better than a simple mutex?

---

### Card 88
**Front:** What is a permit leak and how do you prevent it in request paths?

---

### Card 89
**Front:** Why should scarce-resource acquisition use timeout instead of infinite wait?

---

### Card 90
**Front:** What is thread confinement and when does it simplify correctness?

---

### Card 91
**Front:** How do you explain correctness vs coordination vs scarcity in under 30 seconds?

---

### Card 92
**Front:** Which concurrency pitfalls should always be called out in interview wrap-up?

---

## Project-Specific Drills (8 Cards)

### Card 93
**Front:** In Connect Four, why should gravity placement belong to `Board` instead of `Game`?

---

### Card 94
**Front:** Which invariants must `Game.makeMove(player, column)` enforce before board mutation?

---

### Card 95
**Front:** What data do you store in a Connect Four move-history record to support O(1) undo?

---

### Card 96
**Front:** Why is a strategy interface better than if/else branching for Connect Four bot behavior?

---

### Card 97
**Front:** In Amazon Locker, what state transitions occur from deposit to pickup for a valid token?

---

### Card 98
**Front:** Why should Amazon Locker allocation logic be extracted into a policy abstraction?

---

### Card 99
**Front:** What boundary conditions should be tested for `clearExpiredDeposits()` without using sleep?

---

### Card 100
**Front:** How does an injectable clock improve reservation/token TTL testing in Amazon Locker v3?

---

<p align="center">
  <b>Total: 100 Flashcards</b><br>
  <i>OOP: 15 | SOLID: 20 | Composition: 10 | Principles: 10 | UML: 15 | Smells: 10 | Concurrency & Thread-Safety: 12 | Project Drills: 8</i>
</p>
