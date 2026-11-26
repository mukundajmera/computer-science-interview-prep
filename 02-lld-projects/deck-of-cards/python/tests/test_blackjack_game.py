import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'v1-basic')))

from card import Card, Suit, Rank
from deck import Deck
from hand import BlackjackHand
from player import Player
from game import BlackjackGame

def test_deck_creation_and_shuffle_randomness():
    deck1 = Deck()
    deck2 = Deck()

    assert deck1.remaining_cards() == 52

    cards = set()
    while deck1.remaining_cards() > 0:
        cards.add(str(deck1.deal_card()))
    assert len(cards) == 52

    deck2.shuffle()
    deck3 = Deck()
    differs = False
    for _ in range(52):
        if str(deck2.deal_card()) != str(deck3.deal_card()):
            differs = True
            break
    assert differs, "Shuffled deck should differ from unshuffled deck"

def test_dynamic_ace_score_resolution():
    hand = BlackjackHand()

    # Soft 21: Ace + 10
    hand.add_card(Card(Suit.SPADES, Rank.ACE))
    hand.add_card(Card(Suit.HEARTS, Rank.KING))
    assert hand.get_score() == 21
    assert hand.is_blackjack()

    # Multi Ace: Ace + Ace + 9 = 21
    hand.clear()
    hand.add_card(Card(Suit.SPADES, Rank.ACE))
    hand.add_card(Card(Suit.HEARTS, Rank.ACE))
    hand.add_card(Card(Suit.CLUBS, Rank.NINE))
    assert hand.get_score() == 21
    assert not hand.is_blackjack()

    # Hard hand that would bust if Ace was 11: 10 + 5 + Ace = 16
    hand.clear()
    hand.add_card(Card(Suit.SPADES, Rank.KING))
    hand.add_card(Card(Suit.HEARTS, Rank.FIVE))
    hand.add_card(Card(Suit.CLUBS, Rank.ACE))
    assert hand.get_score() == 16

    # 4 Aces
    hand.clear()
    hand.add_card(Card(Suit.SPADES, Rank.ACE))
    hand.add_card(Card(Suit.HEARTS, Rank.ACE))
    hand.add_card(Card(Suit.CLUBS, Rank.ACE))
    hand.add_card(Card(Suit.DIAMONDS, Rank.ACE))
    assert hand.get_score() == 14

def test_natural_blackjack_detection():
    hand = BlackjackHand()
    hand.add_card(Card(Suit.SPADES, Rank.ACE))
    hand.add_card(Card(Suit.HEARTS, Rank.JACK))
    assert hand.is_blackjack()

    hand.clear()
    hand.add_card(Card(Suit.SPADES, Rank.ACE))
    hand.add_card(Card(Suit.HEARTS, Rank.NINE))
    assert not hand.is_blackjack()

    hand.clear()
    hand.add_card(Card(Suit.SPADES, Rank.TEN))
    hand.add_card(Card(Suit.HEARTS, Rank.FIVE))
    hand.add_card(Card(Suit.CLUBS, Rank.SIX))
    assert hand.get_score() == 21
    assert not hand.is_blackjack()

def test_complete_round_simulation_dealer_drawing():
    game = BlackjackGame()
    p1 = Player("Bob", 1000)
    game.add_player(p1)

    p1.place_bet(100)
    game.start_round()

    assert p1.balance == 900
    assert len(p1.hand.cards) == 2
    assert len(game.dealer_hand.cards) == 2

    game.play_dealer_turn()
    assert game.dealer_hand.get_score() >= 17

    game.settle_bets()
    assert p1.balance >= 900
