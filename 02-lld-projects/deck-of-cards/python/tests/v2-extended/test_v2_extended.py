import pytest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'v2-extended')))

for mod in ['hand', 'card', 'game', 'player', 'deck']:
    if mod in sys.modules:
        del sys.modules[mod]

from card import Card, Rank, Suit
from hand import BlackjackHand
from game import BlackjackGame, GameState
from player import Player

def test_soft_17_detection():
    hand = BlackjackHand()
    hand.add_card(Card(Suit.HEARTS, Rank.ACE))
    hand.add_card(Card(Suit.CLUBS, Rank.SIX))
    
    assert hand.get_score() == 17
    assert hand.is_soft() is True

def test_hard_17_detection():
    hand = BlackjackHand()
    hand.add_card(Card(Suit.HEARTS, Rank.TEN))
    hand.add_card(Card(Suit.CLUBS, Rank.SEVEN))
    
    assert hand.get_score() == 17
    assert hand.is_soft() is False

def test_soft_to_hard_conversion():
    hand = BlackjackHand()
    hand.add_card(Card(Suit.HEARTS, Rank.ACE))
    hand.add_card(Card(Suit.CLUBS, Rank.SIX))
    
    assert hand.get_score() == 17
    assert hand.is_soft() is True
    
    hand.add_card(Card(Suit.SPADES, Rank.TEN))
    assert hand.get_score() == 17
    assert hand.is_soft() is False

def test_hand_comparison():
    hand1 = BlackjackHand()
    hand1.add_card(Card(Suit.HEARTS, Rank.TEN))
    hand1.add_card(Card(Suit.CLUBS, Rank.NINE)) # 19
    
    hand2 = BlackjackHand()
    hand2.add_card(Card(Suit.HEARTS, Rank.TEN))
    hand2.add_card(Card(Suit.CLUBS, Rank.EIGHT)) # 18
    
    assert hand1 > hand2
    assert hand2 < hand1
    
    hand3 = BlackjackHand()
    hand3.add_card(Card(Suit.HEARTS, Rank.TEN))
    hand3.add_card(Card(Suit.CLUBS, Rank.NINE)) # 19
    
    assert hand1 == hand3

def test_blackjack_beats_21():
    bj_hand = BlackjackHand()
    bj_hand.add_card(Card(Suit.HEARTS, Rank.ACE))
    bj_hand.add_card(Card(Suit.CLUBS, Rank.TEN)) # 21 (Blackjack)
    
    reg_21 = BlackjackHand()
    reg_21.add_card(Card(Suit.HEARTS, Rank.TEN))
    reg_21.add_card(Card(Suit.CLUBS, Rank.SIX))
    reg_21.add_card(Card(Suit.SPADES, Rank.FIVE)) # 21 (Not Blackjack)
    
    assert bj_hand > reg_21
    assert reg_21 < bj_hand
