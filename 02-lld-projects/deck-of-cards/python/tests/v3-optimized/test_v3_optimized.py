import pytest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'v3-optimized')))

for mod in ['hand', 'card', 'game', 'player', 'deck']:
    if mod in sys.modules:
        del sys.modules[mod]

from card import Card, Rank, Suit
from hand import BlackjackHand
from game import BlackjackGame, GameState
from player import Player
from deck import Deck

def test_split_mechanic():
    player = Player("Alice", 100)
    player.place_bet(10)
    
    # Force a split hand
    hand = player.hands[0]
    hand.add_card(Card(Suit.HEARTS, Rank.EIGHT))
    hand.add_card(Card(Suit.CLUBS, Rank.EIGHT))
    
    assert hand.can_split() is True
    
    game = BlackjackGame()
    game.add_player(player)
    game._state = GameState.PLAYER_TURNS
    
    # Need cards to deal for the split
    game._deck._cards = [Card(Suit.HEARTS, Rank.TEN), Card(Suit.CLUBS, Rank.TEN), Card(Suit.SPADES, Rank.TEN)]
    game._deck._deal_index = 0

    game.split(player, 0)
    
    assert len(player.hands) == 2
    assert player.balance == 80 # 100 - 10 (initial) - 10 (split)
    assert player.hands[0].bet == 10
    assert player.hands[1].bet == 10
    assert len(player.hands[0].cards) == 2
    assert len(player.hands[1].cards) == 2

def test_double_down_mechanic():
    player = Player("Bob", 100)
    player.place_bet(10)
    
    hand = player.hands[0]
    hand.add_card(Card(Suit.HEARTS, Rank.FIVE))
    hand.add_card(Card(Suit.CLUBS, Rank.SIX))
    
    game = BlackjackGame()
    game.add_player(player)
    game._state = GameState.PLAYER_TURNS
    
    # Mock dealer hand so play_dealer_turn (triggered by advance_to_next_hand) doesn't run indefinitely
    game._dealer_hand.add_card(Card(Suit.HEARTS, Rank.TEN))
    game._dealer_hand.add_card(Card(Suit.CLUBS, Rank.EIGHT))
    game._deck._cards = [Card(Suit.SPADES, Rank.TEN), Card(Suit.DIAMONDS, Rank.TEN)]
    game._deck._deal_index = 0

    game.double_down(player, 0)
    
    assert len(player.hands[0].cards) == 3
    # Note: after double down, the player's turn is over, so the dealer turn plays, and bets are settled!
    # Initial balance: 100. place_bet(10) -> balance = 90.
    # double_down -> balance = 80. Hand total is 5+6+10 = 21.
    # Dealer has 10+8 = 18. Player wins!
    # Win = bet * 2.0 = 20 * 2.0 = 40.
    # Balance = 80 + 40 = 120.
    assert player.balance == 120
    assert player.hands[0].bet == 0 # bet is reset after settlement
    assert player.hands[0].has_doubled is True

def test_insurance_mechanic():
    player = Player("Charlie", 100)
    player.place_bet(10)
    
    game = BlackjackGame()
    game.add_player(player)
    
    # Fake dealer Ace
    game.dealer_hand.add_card(Card(Suit.HEARTS, Rank.ACE))
    game.dealer_hand.add_card(Card(Suit.CLUBS, Rank.TEN)) # Blackjack
    
    game._state = GameState.INSURANCE
    game.offer_insurance(player, 5)
    
    assert player.balance == 85
    assert player.insurance_bet == 5
    
    game.close_insurance()
    
    # Player wins insurance (2:1), loses main hand (because dealer has blackjack and player doesn't)
    assert game._state == GameState.BETTING
    # Balance: 85 + 15 (insurance win) = 100
    assert player.balance == 100

def test_multi_player_state_machine():
    p1 = Player("P1", 100)
    p2 = Player("P2", 100)
    
    p1.place_bet(10)
    p2.place_bet(10)
    
    game = BlackjackGame()
    game.add_player(p1)
    game.add_player(p2)
    
    # Mock deck and dealer so we control the state
    game._deck.shuffle()
    game._state = GameState.PLAYER_TURNS
    
    p1.hands[0].add_card(Card(Suit.HEARTS, Rank.TEN))
    p1.hands[0].add_card(Card(Suit.CLUBS, Rank.SIX))
    
    p2.hands[0].add_card(Card(Suit.SPADES, Rank.TEN))
    p2.hands[0].add_card(Card(Suit.DIAMONDS, Rank.SEVEN))
    
    game._dealer_hand.add_card(Card(Suit.HEARTS, Rank.TEN))
    game._dealer_hand.add_card(Card(Suit.CLUBS, Rank.EIGHT))
    
    # Need sufficient cards in deck for dealer's turn
    game._deck._cards = [Card(Suit.HEARTS, Rank.TEN), Card(Suit.CLUBS, Rank.TEN), Card(Suit.SPADES, Rank.TEN)]
    game._deck._deal_index = 0

    # P1 hits and busts
    game.hit(p1, 0)
    assert p1.hands[0].is_bust() is True
    
    # Should automatically advance to P2
    assert game._current_player_index == 1
    
    # P2 stands
    game.stand(p2, 0)
    
    # Should automatically play dealer turn and settle
    assert game._state == GameState.BETTING

def test_payout_calculations():
    player = Player("Dave", 100)
    player.place_bet(10)
    
    game = BlackjackGame()
    game.add_player(player)
    game._state = GameState.SETTLEMENT
    
    # Win (1:1)
    player.hands[0].add_card(Card(Suit.HEARTS, Rank.TEN))
    player.hands[0].add_card(Card(Suit.CLUBS, Rank.NINE))
    
    game.dealer_hand.add_card(Card(Suit.SPADES, Rank.TEN))
    game.dealer_hand.add_card(Card(Suit.DIAMONDS, Rank.EIGHT))
    
    game.settle_bets()
    assert player.balance == 110 # 90 + 20
    
    # Blackjack (3:2)
    player.place_bet(10)
    player.hands[0].clear()
    game.dealer_hand.clear()
    game._state = GameState.SETTLEMENT
    
    player.hands[0].add_card(Card(Suit.HEARTS, Rank.ACE))
    player.hands[0].add_card(Card(Suit.CLUBS, Rank.TEN))
    
    game.dealer_hand.add_card(Card(Suit.SPADES, Rank.TEN))
    game.dealer_hand.add_card(Card(Suit.DIAMONDS, Rank.EIGHT))
    
    game.settle_bets()
    assert player.balance == 125 # 100 + 25

