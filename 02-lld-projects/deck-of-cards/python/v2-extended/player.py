from hand import BlackjackHand

class Player:
    def __init__(self, name: str, starting_balance: int):
        self._name = name
        self._balance = starting_balance
        self._hand = BlackjackHand()
        self._current_bet = 0

    @property
    def name(self) -> str:
        return self._name

    @property
    def hand(self) -> BlackjackHand:
        return self._hand

    @property
    def balance(self) -> int:
        return self._balance

    def place_bet(self, amount: int):
        if amount > self._balance:
            raise ValueError("Insufficient balance.")
        self._current_bet = amount
        self._balance -= amount

    def receive_winnings(self, multiplier: float):
        self._balance += int(self._current_bet * multiplier)

    def push_bet(self):
        self._balance += self._current_bet

    def reset_bet(self):
        self._current_bet = 0

    def double_bet(self):
        if self._current_bet > self._balance:
             raise ValueError("Insufficient balance to double down.")
        self._balance -= self._current_bet
        self._current_bet *= 2
