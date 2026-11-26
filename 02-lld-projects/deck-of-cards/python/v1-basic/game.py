from enum import Enum
from typing import List
from deck import Deck
from hand import BlackjackHand
from player import Player

class GameState(Enum):
    BETTING = 1
    DEALING = 2
    PLAYER_TURNS = 3
    DEALER_TURN = 4
    SETTLEMENT = 5

class BlackjackGame:
    def __init__(self):
        self._deck = Deck()
        self._players: List[Player] = []
        self._dealer_hand = BlackjackHand()
        self._state = GameState.BETTING
        self._current_player_index = 0

    def add_player(self, player: Player):
        self._players.append(player)

    def start_round(self):
        if self._state != GameState.BETTING:
            raise ValueError("Must be in BETTING state to start round.")
        
        self._deck.shuffle()
        for p in self._players:
            p.hand.clear()
        self._dealer_hand.clear()

        self._state = GameState.DEALING
        for _ in range(2):
            for p in self._players:
                p.hand.add_card(self._deck.deal_card())
            self._dealer_hand.add_card(self._deck.deal_card())
        
        self._state = GameState.PLAYER_TURNS
        self._current_player_index = 0

    def hit(self, player: Player):
        if self._state != GameState.PLAYER_TURNS:
            raise ValueError("Not currently in player turns phase.")
        if player.hand.is_bust():
            return
        player.hand.add_card(self._deck.deal_card())

    def stand(self, player: Player):
         if self._state != GameState.PLAYER_TURNS:
            raise ValueError("Not currently in player turns phase.")
         # Logic to advance to next player could be here

    def double_down(self, player: Player):
        if self._state != GameState.PLAYER_TURNS:
            raise ValueError("Not currently in player turns phase.")
        if len(player.hand.cards) != 2:
            raise ValueError("Can only double down on initial two cards.")
        player.double_bet()
        player.hand.add_card(self._deck.deal_card())

    def advance_to_dealer(self):
        self._state = GameState.DEALER_TURN

    def play_dealer_turn(self):
        if self._state != GameState.DEALER_TURN:
            self._state = GameState.DEALER_TURN
            
        while self._dealer_hand.get_score() < 17:
            self._dealer_hand.add_card(self._deck.deal_card())
        self._state = GameState.SETTLEMENT

    def settle_bets(self):
        if self._state != GameState.SETTLEMENT:
             self._state = GameState.SETTLEMENT
             
        dealer_score = self._dealer_hand.get_score()
        dealer_bust = self._dealer_hand.is_bust()
        dealer_blackjack = self._dealer_hand.is_blackjack()

        for p in self._players:
            player_hand = p.hand
            if player_hand.is_bust():
                pass # Lost
            elif player_hand.is_blackjack():
                if dealer_blackjack:
                    p.push_bet()
                else:
                    p.receive_winnings(2.5) # 3:2 payout
            elif dealer_bust:
                p.receive_winnings(2.0) # 1:1 payout
            elif dealer_blackjack:
                pass # Lost
            else:
                player_score = player_hand.get_score()
                if player_score > dealer_score:
                    p.receive_winnings(2.0)
                elif player_score == dealer_score:
                    p.push_bet()
                else:
                    pass # Lost
            p.reset_bet()
            
        self._state = GameState.BETTING

    @property
    def dealer_hand(self) -> BlackjackHand:
        return self._dealer_hand
