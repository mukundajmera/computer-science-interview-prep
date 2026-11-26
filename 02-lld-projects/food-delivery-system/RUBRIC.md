# Evaluation Rubric: Food Delivery System

This rubric is designed for assessing a candidate's Low-Level Design (LLD) for a Food Delivery System.

## 1. Problem Understanding & Requirements (15%)
*   **Excellent**: Clearly identifies actors (Customer, Restaurant, Driver). Extracts both functional (order placement, tracking) and non-functional (concurrency, consistency) requirements. Sets reasonable boundaries (e.g., scoping out live GPS routing).
*   **Good**: Identifies core actors and functional requirements but might miss edge cases or non-functional constraints.
*   **Poor**: Misses key actors or essential flows (e.g., forgets the Driver component).

## 2. Object Identification and Class Design (25%)
*   **Excellent**: Defines clear, single-responsibility entities (`Order`, `Restaurant`, `MenuItem`, `User`). Uses composition (`Order` has `OrderItem`s) and inheritance/interfaces properly. Data fields and access modifiers are correctly applied.
*   **Good**: Identifies most objects but may have some coupled classes or missing minor entities (e.g., no `Cart` or `OrderItem`, just mapping `Menu`s directly to `Order`s).
*   **Poor**: Massive "God classes" (e.g., a `SystemManager` that handles everything). Anemic domain model where classes only have getters/setters and no behavior.

## 3. Application of Design Patterns (30%)
*   **Excellent**: Identifies and correctly implements the **State Pattern** for `Order` lifecycle management. Uses the **Observer Pattern** for notifications to decouple actors. Applies the **Strategy Pattern** for varied pricing or matching algorithms.
*   **Good**: Recognizes the need for patterns but implementation might be slightly flawed (e.g., suggests Observer but implements tight coupling in code). Might use standard `if/else` for state but encapsulates it well.
*   **Poor**: No design patterns used. Heavy use of `switch`/`if-else` blocks for order state changes. High coupling between core entities.

## 4. Concurrency & Edge Case Handling (15%)
*   **Excellent**: Explicitly addresses race conditions (e.g., two drivers accepting the same order). Proposes atomic operations, locks, or optimistic concurrency control. Handles edge cases like order cancellation during delivery.
*   **Good**: Mentions concurrency but proposes naive solutions (e.g., locking the whole system). Identifies some edge cases.
*   **Poor**: Ignores concurrency entirely. Assumes happy-path only.

## 5. Code Quality & UML/Diagramming (15%)
*   **Excellent**: Writes clean, readable, well-structured code (or pseudo-code). Draws clear Class Diagrams and State/Activity Diagrams that match the proposed code.
*   **Good**: Code is mostly clear. Diagrams are present but might be missing some connections or cardinality.
*   **Poor**: Code is messy, unstructured, or syntax-heavy without logic. Diagrams are missing or contradict the code.
