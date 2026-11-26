# Deck of Cards and Blackjack Game - Interview Scoring Rubric

## Scoring Dimensions

| Dimension | Weight | Strong signal |
| :--- | :--- | :--- |
| **Object Modeling** | 25% | Uses Enums for Suit and Rank. Clean separation between generic Deck/Card and Blackjack-specific logic. Uses composition over inheritance appropriately. |
| **Algorithm (Scoring)** | 30% | Correctly handles multiple Aces in a hand dynamically (e.g., A, A, A, 8 = 21). Clean, O(N) scoring logic. |
| **Game Flow Control** | 25% | Handles dealer rules correctly. Manages state properly (busting, natural blackjack payouts). Safe iteration over players. |
| **Extensibility** | 10% | Code structure allows easy addition of multiple decks (shoe) or other card games. |
| **Robustness** | 10% | Deck handles running out of cards. Protects against duplicate dealing. Validates state transitions. |

## Hard Failure Gates
* Incorrect Ace calculation (e.g., busting on multi-Ace hands).
* Dealing duplicate cards (e.g., by not removing dealt cards from the deck).
* Allowing illegal actions after stand/bust.

## Performance Bands
* **Strong Hire**: Flawless object modeling, elegant Ace calculation, robust state management, clear separation of generic vs specific rules.
* **Hire**: Working solution with minor coupling issues. Correct Ace logic but perhaps slightly convoluted.
* **No Hire**: Fails hard gates. Major bugs in scoring or dealing. Spaghetti code for game flow.

## Cross-links
* [Problem Definition](PROBLEM.md)
* [Design](DESIGN.md)
