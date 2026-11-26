"""
Demo for Tic-Tac-Toe v1 Basic.
"""
from mark import Mark
from player import HumanPlayer
from game import Game


def main():
    """Run the Tic-Tac-Toe demo."""
    print("=" * 44)
    print("       TIC-TAC-TOE - v1 Basic")
    print("=" * 44)
    
    # Create players
    player1 = HumanPlayer("Player 1", Mark.X)
    player2 = HumanPlayer("Player 2", Mark.O)
    
    # Create and play game
    game = Game(player1, player2)
    game.play()
    
    print("\nThanks for playing!")


if __name__ == "__main__":
    main()
