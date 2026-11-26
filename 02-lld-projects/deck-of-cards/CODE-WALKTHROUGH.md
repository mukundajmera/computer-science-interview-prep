# Deck of Cards and Blackjack Game - Code Walkthrough

## End-to-End Trace

1. **Initialization**:
   * The `BlackjackGame` is instantiated with a list of `Player`s.
   * A `Deck` is created. Its constructor iterates through all `Suit`s and `Rank`s, instantiating 52 `Card`s.

2. **Game Round Start**:
   * The `BlackjackGame.playRound()` method is invoked.
   * The `Deck` is shuffled using the Fisher-Yates algorithm.
   * Players place their bets.

3. **Dealing Phase**:
   * Two cards are popped from the `Deck` and added to each `Player`'s `BlackjackHand`.
   * Two cards are given to the `dealerHand`.

4. **Player Turn**:
   * The game iterates over each `Player`.
   * The `Player` evaluates their `BlackjackHand.getScore()`.
   * If a player chooses to "Hit", a card is popped from the `Deck` and added to their hand.
   * `BlackjackHand.getScore()` calculates the value. It sums the points, initially treating Aces as 11. If the score exceeds 21, it subtracts 10 for each Ace until the score is $\le 21$ or all Aces have been counted as 1.

5. **Dealer Turn**:
   * The dealer reveals their hand and checks their score.
   * While `dealerHand.getScore() < 17`, the dealer draws a card from the `Deck`.

6. **Settlement**:
   * The game compares each `Player`'s `BlackjackHand` score against the `dealerHand` score.
   * Payouts or collections are processed based on the comparison (Win, Loss, Push, or Natural Blackjack).
   * All hands are cleared for the next round.
