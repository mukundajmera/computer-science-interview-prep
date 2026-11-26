from typing import List
from hand import BlackjackHand

class Player:
    def __init__(self, name: str, balance: float):
        self._name = name
        self._balance = balance
        self._hands: List[BlackjackHand] = [BlackjackHand(bet=0.0)]
        self._insurance_bet = 0.0

    @property
    def name(self) -> str:
        return self._name

    @property
    def balance(self) -> float:
        return self._balance

    @property
    def hands(self) -> List[BlackjackHand]:
        return self._hands
        
    @property
    def insurance_bet(self) -> float:
        return self._insurance_bet

    def clear_hands(self):
        primary_bet = self._hands[0].bet if self._hands else 0.0
        self._hands = [BlackjackHand(bet=primary_bet)]
        self._insurance_bet = 0.0

    def place_bet(self, amount: float, hand_index: int = 0):
        if amount > self._balance:
             raise ValueError("Insufficient balance.")
        self._balance -= amount
        self._hands[hand_index].bet += amount
        
    def place_insurance_bet(self, amount: float):
        if amount > self._balance:
             raise ValueError("Insufficient balance.")
        self._balance -= amount
        self._insurance_bet += amount
        
    def win_insurance(self):
        self._balance += self._insurance_bet * 3 # 2:1 payout + original bet returned
        self._insurance_bet = 0.0

    def double_bet(self, hand_index: int = 0):
        current_bet = self._hands[hand_index].bet
        if current_bet > self._balance:
            raise ValueError("Insufficient balance to double.")
        self._balance -= current_bet
        self._hands[hand_index].bet += current_bet

    def receive_winnings(self, multiplier: float, hand_index: int = 0):
        self._balance += self._hands[hand_index].bet * multiplier

    def push_bet(self, hand_index: int = 0):
        self._balance += self._hands[hand_index].bet
        
    def add_split_hand(self, bet: float) -> BlackjackHand:
        if bet > self._balance:
            raise ValueError("Insufficient balance for split.")
        self._balance -= bet
        new_hand = BlackjackHand(bet=bet)
        self._hands.append(new_hand)
        return new_hand

