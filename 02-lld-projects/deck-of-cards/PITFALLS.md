# Deck of Cards and Blackjack Game - Common Pitfalls

## 1. Static Card Points
* **Signal**: Assigning a fixed point value to the `Card` or `Rank` enum that ignores context.
* **Root Cause**: Failing to recognize that in Blackjack, Ace values are dynamic and depend on the *entire hand*, not just the card itself.
* **Mitigation**: Move scoring logic out of the `Card` class and into a game-specific `Hand` evaluator (e.g., `BlackjackHand`).
* **Validation**: Write tests for hands with multiple Aces (e.g., A + A + 9 = 21).

## 2. Mutable Deck Instances Corrupting Dealing Order
* **Signal**: Reusing a `Deck` array without tracking the current index, or incorrectly handling indices during shuffling, leading to duplicated or dropped cards.
* **Root Cause**: Poor understanding of array/list manipulation or reference semantics in the chosen language.
* **Mitigation**: Use a standard Library stack or queue to draw cards, or maintain a strict `dealIndex` pointer that increments on every deal.
* **Validation**: Assert that drawing 52 cards results in exactly 52 unique cards and that drawing the 53rd throws an exception.

## 3. Tight Coupling of Game Rules
* **Signal**: Putting Blackjack dealer AI or payout rules inside the `Deck` or `Card` class.
* **Root Cause**: Lack of single responsibility principle (SRP).
* **Mitigation**: Create separate classes for `GameEngine`, `Dealer`, and `Player`.
* **Validation**: Ask "Could I use this `Deck` to play Poker without modification?"

## 4. Non-thread-safe Shoe Access
* **Signal**: In a multiplayer online casino scenario, multiple table threads drawing from a shared shoe without synchronization.
* **Root Cause**: Ignoring concurrency.
* **Mitigation**: Ensure atomic draws from the shoe, perhaps using concurrent queues or locks.
