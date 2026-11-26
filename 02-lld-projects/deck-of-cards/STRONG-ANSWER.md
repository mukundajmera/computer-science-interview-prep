# Strong Answer: Deck of Cards & Blackjack

**Time Target:** 45 minutes

## 1. Requirements Clarification & Pacing
**Say:** "To model a Deck of Cards and a game like Blackjack, I need to design for correctness, extensibility, and state management. Before diving in, I want to clarify a few boundaries:
*   **Scale & Limits:** Are we simulating a single deck or a multi-deck 'shoe'? The standard game often uses 1–8 decks. I will design the `Deck` class to support multiple decks to increase the house edge or match casino standards.
*   **Action Scope:** I will focus on standard Blackjack mechanics: Hit, Stand, Double Down, and Split. Advanced rules like Surrender will be omitted for simplicity but structurally permitted by our state machine.
*   **State Machine:** The game proceeds in strict phases: Betting, Dealing, Player Turns, Dealer Turn, and Settlement. Ensuring safe transitions is paramount."

## 2. Entities & APIs
**Say:** "The core entities will be separated into the domain layer (Cards) and the application layer (Blackjack Game).

**Domain Entities:**
*   `Suit` (Enum) and `Rank` (Enum): Immutably define the 52 cards.
*   `Card`: Combines Suit and Rank.
*   `Deck`: Maintains a list of `Card`s and an index to deal in O(1) time rather than popping and resizing the array.
*   `Hand`: Base class containing a list of `Card`s.
*   `BlackjackHand`: Extends `Hand` with scoring logic (Aces as 1 or 11), soft checks, and comparison semantics.

**Game Entities:**
*   `Player`: Manages balance, `currentBet`, and a `BlackjackHand`.
*   `BlackjackGame`: Orchestrator managing a `Deck`, a list of `Player`s, a `dealerHand`, and the current `GameState`.
*   `GameState` (Enum): Controls flow (BETTING, DEALING, PLAYER_TURNS, DEALER_TURN, SETTLEMENT).

**Key Public APIs:**
Both Java and Python implement the following core operations:
```java
// Java API
public void startRound();
public void hit(Player p);
public void stand(Player p);
public void doubleDown(Player p);
public void playDealerTurn();
public void settleBets();
```
```python
# Python API
def start_round(self): pass
def hit(self, player: Player): pass
def stand(self, player: Player): pass
def double_down(self, player: Player): pass
def play_dealer_turn(self): pass
def settle_bets(self): pass
```"

## 3. Correctness & Complexity
**Say:** "The most critical logic in Blackjack is Ace evaluation. In `BlackjackHand.getScore()`, I count the sum of all cards assuming Aces are 11. If the sum exceeds 21, I decrement the score by 10 for each Ace until the score is $\le 21$ or no Aces remain. This executes in O(N) time where N is the number of cards in the hand (typically bounded).

For dealing cards, `Deck.dealCard()` executes in O(1) by incrementing a pointer rather than popping from the front of an array. Shuffling uses an O(N) algorithm (e.g. Fisher-Yates)."

## 4. Design Alternatives & Trade-offs
**Say:** "There are a few design trade-offs:
1.  **Immutability vs Mutation:** `Card` instances are immutable and cached. `Hand` mutates its list of cards. Recreating immutable hands on every hit would be functional but incurs unnecessary GC overhead.
2.  **Deck Data Structure:** Using a Stack vs Array with Pointer. I chose a pre-allocated Array/List with a `dealIndex`. This avoids constant resizing and object allocation during dealing and reshuffling.
3.  **Inheritance vs Composition:** `BlackjackHand` extends `Hand`, treating `Hand` as a common base for Poker or Hearts later."

## 5. Edge Cases & Reference Contracts
**Say:** "To ensure robustness, I explicitly handle edge cases matching our reference contracts. Both languages mirror these safety boundaries:

*   **Normal use-case:** A standard game progresses sequentially: Betting -> Dealing -> Player Turns -> Dealer Turn -> Settlement.
```java
// Java
public void startRound() {
    // ...
    state = GameState.DEALING;
    for (int i = 0; i < 2; i++) {
        for (Player p : players) {
            p.getHand().addCard(deck.dealCard());
        }
        dealerHand.addCard(deck.dealCard());
    }
    state = GameState.PLAYER_TURNS;
}
```
```python
# Python
def start_round(self):
    # ...
    self._state = GameState.DEALING
    for _ in range(2):
        for p in self._players:
            p.hand.add_card(self._deck.deal_card())
        self._dealer_hand.add_card(self._deck.deal_card())
    
    self._state = GameState.PLAYER_TURNS
    self._current_player_index = 0
```
*   **Empty/invalid input:** 
```java
// Java
public void startRound() {
    if (state != GameState.BETTING) {
        throw new IllegalStateException("Must be in BETTING state to start round.");
    }
    // ...
```
```python
# Python
def start_round(self):
    if self._state != GameState.BETTING:
        raise ValueError("Must be in BETTING state to start round.")
    # ...
```
*   **Duplicate operation:** A duplicate `doubleDown` fails safely:
```java
// Java
public void doubleDown(Player p) {
    if (state != GameState.PLAYER_TURNS) {
        throw new IllegalStateException("Not currently in player turns phase.");
    }
    if (p.getHand().getCards().size() != 2) {
        throw new IllegalStateException("Can only double down on initial two cards.");
    }
    // ...
}
```
```python
# Python
def double_down(self, player: Player):
    if self._state != GameState.PLAYER_TURNS:
        raise ValueError("Not currently in player turns phase.")
    if len(player.hand.cards) != 2:
        raise ValueError("Can only double down on initial two cards.")
    # ...
```
*   **Capacity boundary:** Deck limits are validated. An empty shoe will halt drawing until a reshuffle.
```java
// Java
public Card dealCard() {
    if (dealIndex >= cards.size()) {
        throw new IllegalStateException("No cards left in the deck.");
    }
    return cards.get(dealIndex++);
}
```
```python
# Python
def deal_card(self) -> Card:
    if self._deal_index >= len(self._cards):
        raise ValueError("No cards left in the deck.")
    card = self._cards[self._deal_index]
    self._deal_index += 1
    return card
```
*   **Failure rollback:** Insufficient funds during a bet modification rolls back before state changes:
```java
// Java
public void doubleBet() {
    if (currentBet > balance) {
        throw new IllegalArgumentException("Insufficient balance to double down.");
    }
    this.balance -= this.currentBet;
    this.currentBet *= 2;
}
```
```python
# Python
def double_bet(self):
    if self._current_bet > self._balance:
         raise ValueError("Insufficient balance to double down.")
    self._balance -= self._current_bet
    self._current_bet *= 2
```"

## 6. Version-Specific Feature Deltas
**Say:** "Compared to v1 of our basic card simulator, the v2 extended release focuses heavily on game state orchestration. Version-specific feature deltas include the transition from a stateless `Deck` to a fully state-managed `BlackjackGame` with strict `GameState` enforcement, thread-safe `doubleDown` mechanics, dealer 'soft 17' logic, and detailed settlement rules. Focused tests strictly target this version (e.g., `test_soft_17_detection` and `test_soft_to_hard_conversion` in Python, and `testSoft17Detection` in Java), rather than silently importing v1 tests. This ensures our acceptance criteria for version-specific feature deltas are verifiably met."

## 7. Failure Handling & Concurrency Defense
**Say:** "In a concurrent environment (e.g., an online casino server supporting many tables), thread safety is essential.
1.  **State Rollback:** As mentioned in the failure rollback, if a network failure or validation error occurs during `doubleDown()`, the player's balance must be refunded before failing the request.
2.  **Concurrency:** A `BlackjackGame` instance is not inherently thread-safe. If multiple API requests (e.g., Hit and Stand) arrive simultaneously for the same game, it could corrupt the state. I would use a lock on the `BlackjackGame` instance to serialize all actions for a specific table. This guarantees deterministic transitions and prevents race conditions."
