from typing import List
from card import Card, Rank

class Hand:
    def __init__(self):
        self._cards: List[Card] = []

    def add_card(self, card: Card):
        self._cards.append(card)

    @property
    def cards(self) -> List[Card]:
        return list(self._cards)

    def clear(self):
        self._cards.clear()


class BlackjackHand(Hand):
    def __init__(self, bet: float = 0.0):
        super().__init__()
        self.bet = bet
        self.is_stand = False
        self.has_doubled = False
        
    def get_score(self) -> int:
        score = 0
        ace_count = 0

        for card in self._cards:
            if card.rank == Rank.ACE:
                ace_count += 1
                score += 11
            else:
                score += card.rank.blackjack_value

        while score > 21 and ace_count > 0:
            score -= 10
            ace_count -= 1

        return score

    def is_soft(self) -> bool:
        score = 0
        ace_count = 0

        for card in self._cards:
            if card.rank == Rank.ACE:
                ace_count += 1
                score += 11
            else:
                score += card.rank.blackjack_value

        while score > 21 and ace_count > 0:
            score -= 10
            ace_count -= 1

        return ace_count > 0

    def is_bust(self) -> bool:
        return self.get_score() > 21

    def is_blackjack(self) -> bool:
        return len(self._cards) == 2 and self.get_score() == 21

    def can_split(self) -> bool:
        return len(self._cards) == 2 and self._cards[0].rank.blackjack_value == self._cards[1].rank.blackjack_value

    def __eq__(self, other):
        if not isinstance(other, BlackjackHand):
            return NotImplemented
        return self._compare_value() == other._compare_value()
        
    def __lt__(self, other):
        if not isinstance(other, BlackjackHand):
            return NotImplemented
        return self._compare_value() < other._compare_value()

    def _compare_value(self) -> float:
        if self.is_bust():
            return -1
        if self.is_blackjack():
            return 22
        return self.get_score()
