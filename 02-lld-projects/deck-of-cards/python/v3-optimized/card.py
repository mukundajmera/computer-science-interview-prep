from enum import Enum

class Suit(Enum):
    CLUBS = 1
    DIAMONDS = 2
    HEARTS = 3
    SPADES = 4

class Rank(Enum):
    TWO = 2
    THREE = 3
    FOUR = 4
    FIVE = 5
    SIX = 6
    SEVEN = 7
    EIGHT = 8
    NINE = 9
    TEN = 10
    JACK = 11
    QUEEN = 12
    KING = 13
    ACE = 1

    @property
    def blackjack_value(self) -> int:
        if self in (Rank.JACK, Rank.QUEEN, Rank.KING):
            return 10
        if self == Rank.ACE:
            return 1
        return self.value

class Card:
    def __init__(self, suit: Suit, rank: Rank):
        self._suit = suit
        self._rank = rank

    @property
    def suit(self) -> Suit:
        return self._suit

    @property
    def rank(self) -> Rank:
        return self._rank

    def __str__(self) -> str:
        return f"{self._rank.name} of {self._suit.name}"

    def __repr__(self) -> str:
        return self.__str__()
