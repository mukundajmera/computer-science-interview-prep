# Deck of Cards and Blackjack Game - Follow-Up Questions

## Follow-up questions
* How would you implement card counting tracking (e.g., the Hi-Lo system)?
* How would you support split hands, including the specific restrictions on splitting Aces (often only one additional card is allowed)?
* How would you implement an "Insurance" betting feature against a dealer's Ace?

## Variants and extensions
* **Multi-deck Shoe**: Extend the game to use 6 or 8 decks shuffled together.
* **Poker Extension**: Reuse the `Card` and `Deck` classes to implement a Poker hand evaluator.

## Interviewer probes to prepare
* "What happens if the deck runs out of cards in the middle of a hand?"
* "Show me how your scoring algorithm handles a hand with 4 Aces and a 7."
* "How would you handle a multiplayer scenario where players act concurrently vs sequentially?"
