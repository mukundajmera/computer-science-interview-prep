# Deck of Cards and Blackjack Game - Design

## Cross-links
* [Problem Definition](PROBLEM.md)
* [Approach](APPROACH.md)
* [Code Walkthrough](CODE-WALKTHROUGH.md)

## System Architecture

The core architecture separates the generic card components from the Blackjack-specific rules.

* **Core Models**: `Suit`, `Rank`, `Card`, `Deck`, `Hand`.
* **Game Specific**: `BlackjackHand`, `Player`, `Dealer`, `BlackjackGame`.

## Class Diagram

```mermaid
classDiagram
    class Suit {
        <<enumeration>>
        CLUBS, DIAMONDS, HEARTS, SPADES
    }
    class Rank {
        <<enumeration>>
        TWO, THREE, FOUR, ..., KING, ACE
    }
    class Card {
        -Suit suit
        -Rank rank
        +getSuit() Suit
        +getRank() Rank
    }
    class Deck {
        -List~Card~ cards
        +shuffle()
        +dealCard() Card
    }
    class Hand {
        #List~Card~ cards
        +addCard(Card c)
        +getCards() List~Card~
        +clear()
    }
    class BlackjackHand {
        +getScore() int
        +isBust() boolean
        +isBlackjack() boolean
    }
    class Player {
        -String name
        -BlackjackHand hand
        -int balance
        -int currentBet
        +placeBet(int amount)
        +receiveWinnings(int amount)
    }
    class BlackjackGame {
        -Deck deck
        -List~Player~ players
        -BlackjackHand dealerHand
        +playRound()
    }

    Card --> Suit
    Card --> Rank
    Deck "1" o-- "many" Card
    Hand "1" o-- "many" Card
    BlackjackHand --|> Hand
    Player "1" *-- "1" BlackjackHand
    BlackjackGame --> Deck
    BlackjackGame "1" *-- "many" Player
```

## Sequence Diagram (Full Round)

```mermaid
sequenceDiagram
    participant Game
    participant Player
    participant Dealer
    participant Deck

    Game->>Deck: shuffle()
    Game->>Player: placeBet()
    
    rect rgb(200, 200, 200)
    Note over Game, Deck: Dealing Phase
    Game->>Deck: dealCard()
    Deck-->>Game: Card
    Game->>Player: addCard()
    Game->>Deck: dealCard()
    Game->>Dealer: addCard() (Face up)
    Game->>Deck: dealCard()
    Game->>Player: addCard()
    Game->>Deck: dealCard()
    Game->>Dealer: addCard() (Face down)
    end

    rect rgb(220, 220, 255)
    Note over Game, Player: Player Turn
    loop Until Stand or Bust
        Game->>Player: promptAction()
        alt Hit
            Player->>Game: hit
            Game->>Deck: dealCard()
            Game->>Player: addCard()
        else Stand
            Player->>Game: stand
        end
    end
    end

    rect rgb(255, 220, 220)
    Note over Game, Dealer: Dealer Turn
    loop Until Score >= 17
        Game->>Deck: dealCard()
        Game->>Dealer: addCard()
    end
    end

    Note over Game, Player: Settlement Phase
    Game->>Game: resolveBets()
    Game->>Player: payout() / collect()
```

## Patterns
* **State Pattern**: The `BlackjackGame` naturally flows through states (Betting, Dealing, PlayerTurns, DealerTurn, Settlement). Although simple implementations might use sequential methods, complex multi-player flows benefit from a State machine.
* **Template Method Pattern**: A base `Game` class could define the skeleton `play()` algorithm, delegating specific rules (like `checkWinCondition`) to subclasses like `BlackjackGame` or `PokerGame`.
* **Strategy Pattern**: Dealer AI uses a fixed strategy (Hit until 17). Players could theoretically be automated using strategies.
