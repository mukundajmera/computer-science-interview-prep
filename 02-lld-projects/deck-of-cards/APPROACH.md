# Deck of Cards and Blackjack Game - Approach

## Entity Identification
The system models real-world entities found in a card game: `Card`, `Suit`, `Rank`, `Deck`, `Hand`, `Player`, and the `Game` itself.

## Inheritance vs Composition for Card Games
Instead of building a rigid hierarchy of specific games inheriting from a base game, we use composition.
A `BlackjackGame` uses a `Deck` and multiple `Player`s.
A `BlackjackHand` extends a base `Hand` to provide game-specific scoring logic. This keeps the base `Card` and `Deck` implementations clean and game-agnostic, allowing them to be reused for Poker, Hearts, etc.

## Ace Valuation Dynamic Reduction Algorithm
Blackjack scoring requires a dynamic approach to handle Aces. The `BlackjackHand` calculates a base score treating all Aces as 11. It also tracks the number of Aces in the hand.
If the total score exceeds 21 and there are Aces present, the algorithm reduces the score by 10 for each Ace until the score is 21 or less, or there are no more "soft" Aces.

## Player Turn and Betting Round State Transitions
The game follows a state machine flow:
1. **Betting**: Players place bets before cards are dealt.
2. **Dealing**: Initial cards are distributed (two to each player, two to the dealer).
3. **Player Turns**: Each player takes actions (Hit, Stand, Double Down) until they bust or stand.
4. **Dealer Turn**: The dealer reveals their hidden card and draws according to fixed rules (hit until >= 17).
5. **Settlement**: Win/loss/push conditions are evaluated, and payouts are handled.

## Multi-Deck Shoe Management
To support professional Blackjack rules and prevent card counting, a "shoe" composed of multiple decks is used. Our `Deck` class can be generalized or composed to hold $N \times 52$ cards, which are shuffled together.
