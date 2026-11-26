"""
Snake and Ladder Game - V1 Basic Demo
"""
from game import Game


def main():
    print("==========================================")
    print("   Snake and Ladder Game - V1 Basic Demo")
    print("==========================================\n")
    
    # Create game with standard board
    game = Game()
    
    # Add players
    game.add_player("Alice")
    game.add_player("Bob")
    game.add_player("Charlie")
    
    # Play the game
    print("\n--- Starting Game ---")
    winner = game.play_game()
    
    if winner:
        print(f"\nFinal Winner: {winner.name}")
    
    print("\n--- Demo Complete ---")


if __name__ == "__main__":
    main()
