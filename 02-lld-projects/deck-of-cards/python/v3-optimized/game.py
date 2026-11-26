from enum import Enum
from typing import List
from deck import Deck
from hand import BlackjackHand
from player import Player
from card import Rank

class GameState(Enum):
    BETTING = 1
    DEALING = 2
    INSURANCE = 3
    PLAYER_TURNS = 4
    DEALER_TURN = 5
    SETTLEMENT = 6

class BlackjackGame:
    def __init__(self):
        self._deck = Deck()
        self._players: List[Player] = []
        self._dealer_hand = BlackjackHand()
        self._state = GameState.BETTING
        self._current_player_index = 0
        self._current_hand_index = 0

    def add_player(self, player: Player):
        self._players.append(player)

    def start_round(self):
        if self._state != GameState.BETTING:
            raise ValueError("Must be in BETTING state to start round.")
        
        self._deck.shuffle()
        for p in self._players:
            p.clear_hands()
        self._dealer_hand.clear()

        self._state = GameState.DEALING
        for _ in range(2):
            for p in self._players:
                p.hands[0].add_card(self._deck.deal_card())
            self._dealer_hand.add_card(self._deck.deal_card())
            
        # Check if dealer's upcard is an Ace for insurance
        if self._dealer_hand.cards[0].rank == Rank.ACE:
            self._state = GameState.INSURANCE
        else:
            self._state = GameState.PLAYER_TURNS
            
        self._current_player_index = 0
        self._current_hand_index = 0
        self._advance_if_needed()
        
    def offer_insurance(self, player: Player, amount: float):
        if self._state != GameState.INSURANCE:
            raise ValueError("Not currently in insurance phase.")
        player.place_insurance_bet(amount)
        
    def close_insurance(self):
        if self._state != GameState.INSURANCE:
            raise ValueError("Not currently in insurance phase.")
        # Dealer checks for blackjack
        if self._dealer_hand.is_blackjack():
            for p in self._players:
                if p.insurance_bet > 0:
                    p.win_insurance()
            self._state = GameState.SETTLEMENT
            self.settle_bets()
        else:
            # Insurance bets lost, proceed to player turns
            for p in self._players:
                p._insurance_bet = 0.0
            self._state = GameState.PLAYER_TURNS
            self._advance_if_needed()

    def hit(self, player: Player, hand_index: int = 0):
        if self._state != GameState.PLAYER_TURNS:
            raise ValueError("Not currently in player turns phase.")
        if player != self._players[self._current_player_index] or hand_index != self._current_hand_index:
            raise ValueError("Not this player's/hand's turn.")
            
        hand = player.hands[hand_index]
        if hand.is_bust() or hand.is_stand or hand.has_doubled:
            return
            
        hand.add_card(self._deck.deal_card())
        self._advance_if_needed()

    def stand(self, player: Player, hand_index: int = 0):
        if self._state != GameState.PLAYER_TURNS:
            raise ValueError("Not currently in player turns phase.")
        if player != self._players[self._current_player_index] or hand_index != self._current_hand_index:
            raise ValueError("Not this player's/hand's turn.")
            
        hand = player.hands[hand_index]
        hand.is_stand = True
        self._advance_to_next_hand()

    def double_down(self, player: Player, hand_index: int = 0):
        if self._state != GameState.PLAYER_TURNS:
            raise ValueError("Not currently in player turns phase.")
        if player != self._players[self._current_player_index] or hand_index != self._current_hand_index:
            raise ValueError("Not this player's/hand's turn.")
            
        hand = player.hands[hand_index]
        if len(hand.cards) != 2:
            raise ValueError("Can only double down on initial two cards.")
            
        player.double_bet(hand_index)
        hand.has_doubled = True
        hand.add_card(self._deck.deal_card())
        self._advance_to_next_hand()
        
    def split(self, player: Player, hand_index: int = 0):
        if self._state != GameState.PLAYER_TURNS:
            raise ValueError("Not currently in player turns phase.")
        if player != self._players[self._current_player_index] or hand_index != self._current_hand_index:
            raise ValueError("Not this player's/hand's turn.")
            
        hand = player.hands[hand_index]
        if not hand.can_split():
            raise ValueError("Cannot split this hand.")
            
        # Move one card to new hand and duplicate bet
        card_to_move = hand._cards.pop()
        new_hand = player.add_split_hand(hand.bet)
        new_hand.add_card(card_to_move)
        
        # Deal one card to both hands
        hand.add_card(self._deck.deal_card())
        new_hand.add_card(self._deck.deal_card())
        
        self._advance_if_needed()

    def _advance_if_needed(self):
        if self._state != GameState.PLAYER_TURNS:
            return
            
        while self._current_player_index < len(self._players):
            player = self._players[self._current_player_index]
            if self._current_hand_index < len(player.hands):
                hand = player.hands[self._current_hand_index]
                if hand.is_bust() or hand.is_stand or hand.has_doubled or hand.is_blackjack():
                    self._current_hand_index += 1
                else:
                    return # Current hand is still active
            else:
                self._current_player_index += 1
                self._current_hand_index = 0
                
        # If we reach here, all players have finished
        self.play_dealer_turn()

    def _advance_to_next_hand(self):
        self._current_hand_index += 1
        self._advance_if_needed()

    def play_dealer_turn(self):
        self._state = GameState.DEALER_TURN
            
        # Hit on soft 17
        while True:
            score = self._dealer_hand.get_score()
            if score < 17 or (score == 17 and self._dealer_hand.is_soft()):
                self._dealer_hand.add_card(self._deck.deal_card())
            else:
                break
                
        self.settle_bets()

    def settle_bets(self):
        self._state = GameState.SETTLEMENT

        for p in self._players:
            for i, player_hand in enumerate(p.hands):
                if player_hand.bet == 0:
                    continue # No bet on this hand
                    
                if player_hand.is_bust():
                    pass # Lost
                elif player_hand.is_blackjack():
                    if self._dealer_hand.is_blackjack():
                        p.push_bet(i)
                    else:
                        p.receive_winnings(2.5, i) # 3:2 payout
                elif self._dealer_hand.is_bust():
                    p.receive_winnings(2.0, i) # 1:1 payout
                elif self._dealer_hand.is_blackjack():
                    pass # Lost
                else:
                    if player_hand > self._dealer_hand:
                        p.receive_winnings(2.0, i)
                    elif player_hand == self._dealer_hand:
                        p.push_bet(i)
                    else:
                        pass # Lost
                player_hand.bet = 0
            
        self._state = GameState.BETTING

    @property
    def dealer_hand(self) -> BlackjackHand:
        return self._dealer_hand
