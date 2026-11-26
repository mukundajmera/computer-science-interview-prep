# Deck of Cards and Blackjack Game - Problem Description

## Functional Requirements
* **Standard Deck**: A deck consists of 52 cards, each having a Suit (Clubs, Diamonds, Hearts, Spades) and a Rank (Two through Ace).
* **Shuffling**: Support shuffling the deck using a random algorithm (e.g., Fisher-Yates).
* **Dealing Cards**: Support dealing a single card from the deck.
* **Blackjack Scoring**:
  * Number cards (2-10) are worth their face value.
  * Face cards (Jack, Queen, King) are worth 10.
  * Aces can be worth 1 or 11, depending on which value provides the best score without exceeding 21.
* **Natural Blackjack Detection**: Detect when a hand initially consists of an Ace and a 10-value card (totaling 21).
* **Betting Round State Machine**: The game progresses through betting, dealing, player turns, dealer turn, and settlement.
* **Dealer Rules**: The dealer must hit until their score is 17 or higher.
* **Player Actions**: Players can Hit (take a card), Stand (end turn), or Double Down (double bet and take exactly one more card).
* **Payout Settlements**: Handle betting and payouts based on the outcome of the game (e.g., 3:2 for Blackjack, 1:1 for regular win).

## Non-Functional Requirements
* **Extensibility**: The core deck and card classes should be reusable for other card games (e.g., Poker, Hearts).
* **Correctness**: The Ace value calculation must accurately reflect the optimal score for any combination of cards.
* **Performance**: Operations like dealing and scoring should be fast (O(1) where possible).

## Constraints
* The application is primarily an in-memory simulation.
* Multiple players should be supported at a single table.

## Clarifying Questions
* **Q**: Do we need to support splitting pairs?
* **A**: No, splitting is an advanced feature and can be omitted for the basic version, but the architecture should be able to support it later.
* **Q**: How many decks are used in Blackjack?
* **A**: A standard game can use one or more decks (a "shoe"). The system should support multiple decks.

## Core Entities
* `Suit`: Enum for Clubs, Diamonds, Hearts, Spades.
* `Rank`: Enum for Two to Ace.
* `Card`: Represents a single playing card.
* `Deck`: A collection of Cards, supporting shuffle and deal operations.
* `Hand`: A collection of Cards held by a player or dealer.
* `BlackjackHand`: A specialized Hand with Blackjack scoring logic.
* `Player`: Represents a participant in the game with a Hand and a balance.
* `BlackjackGame`: Coordinates the flow of the game, managing players, the deck, and rules.
