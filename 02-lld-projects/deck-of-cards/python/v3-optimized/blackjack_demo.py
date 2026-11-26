from player import Player
from game import BlackjackGame

def main():
    game = BlackjackGame()
    p1 = Player("Alice", 1000)
    game.add_player(p1)

    p1.place_bet(100)
    game.start_round()

    print(f"Alice's Hand: {p1.hands[0].cards} (Score: {p1.hands[0].get_score()})")
    print(f"Dealer's Face Up Card: {game.dealer_hand.cards[0]}")

    game.play_dealer_turn()
    print(f"Dealer's Hand: {game.dealer_hand.cards} (Score: {game.dealer_hand.get_score()})")

    game.settle_bets()
    print(f"Alice's Balance: {p1.balance}")

if __name__ == "__main__":
    main()
