import random
from card import Card, Suit, Rank

class Deck:
    def __init__(self):
        self._cards = [Card(suit, rank) for suit in Suit for rank in Rank]
        self._deal_index = 0

    def shuffle(self):
        random.shuffle(self._cards)
        self._deal_index = 0

    def deal_card(self) -> Card:
        if self._deal_index >= len(self._cards):
            raise ValueError("No cards left in the deck.")
        card = self._cards[self._deal_index]
        self._deal_index += 1
        return card

    def remaining_cards(self) -> int:
        return len(self._cards) - self._deal_index
