"""
Chess Game - V1 Basic Demo
"""
from position import Position
from game import Game


def main():
    print("=== Chess Game Demo ===\n")

    game = Game("Alice", "Bob")
    print("Initial board:")
    game.display_board()

    print("\n--- Playing some moves ---\n")

    # 1. e4
    print("1. White plays e2-e4")
    game.make_move(Position.from_algebraic("e2"), Position.from_algebraic("e4"))
    game.display_board()

    # 1... e5
    print("\n1... Black plays e7-e5")
    game.make_move(Position.from_algebraic("e7"), Position.from_algebraic("e5"))
    game.display_board()

    # 2. Nf3
    print("\n2. White plays Nf3")
    game.make_move(Position.from_algebraic("g1"), Position.from_algebraic("f3"))
    game.display_board()

    # Show valid moves
    print("\n--- Valid moves for knight on f3 ---")
    knight_moves = game.get_valid_moves(Position.from_algebraic("f3"))
    print(f"Knight can move to: {[str(m) for m in knight_moves]}")

    print(f"\nCurrent turn: {game.current_turn.value}")
    print(f"Current player: {game.current_player}")

    print("\n=== Demo Complete ===")


if __name__ == "__main__":
    main()
