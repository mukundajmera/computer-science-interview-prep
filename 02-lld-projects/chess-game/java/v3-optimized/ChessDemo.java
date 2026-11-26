import java.util.List;

/**
 * Chess Game - V1 Basic Demo
 * 
 * Demonstrates the chess game in action.
 */
public class ChessDemo {

    public static void main(String[] args) {
        System.out.println("=== Chess Game Demo ===\n");

        // Create a new game
        Game game = new Game("Alice", "Bob");

        System.out.println("Initial board:");
        game.displayBoard();

        // Play some moves
        System.out.println("\n--- Playing some moves ---\n");

        // 1. e4
        System.out.println("1. White plays e2-e4");
        game.makeMove(Position.fromAlgebraic("e2"), Position.fromAlgebraic("e4"));
        game.displayBoard();

        // 1... e5
        System.out.println("\n1... Black plays e7-e5");
        game.makeMove(Position.fromAlgebraic("e7"), Position.fromAlgebraic("e5"));
        game.displayBoard();

        // 2. Nf3
        System.out.println("\n2. White plays Nf3 (knight from g1 to f3)");
        game.makeMove(Position.fromAlgebraic("g1"), Position.fromAlgebraic("f3"));
        game.displayBoard();

        // 2... Nc6
        System.out.println("\n2... Black plays Nc6 (knight from b8 to c6)");
        game.makeMove(Position.fromAlgebraic("b8"), Position.fromAlgebraic("c6"));
        game.displayBoard();

        // 3. Bb5 (Ruy Lopez)
        System.out.println("\n3. White plays Bb5 (bishop from f1 to b5) - Ruy Lopez!");
        game.makeMove(Position.fromAlgebraic("f1"), Position.fromAlgebraic("b5"));
        game.displayBoard();

        // Show valid moves
        System.out.println("\n--- Valid moves for knight on f3 ---");
        List<Position> knightMoves = game.getValidMoves(Position.fromAlgebraic("f3"));
        System.out.println("Knight can move to: " + knightMoves);

        // Test invalid moves
        System.out.println("\n--- Testing invalid moves ---");

        System.out.println("\nTrying to move white piece on black's turn:");
        boolean result = game.makeMove(Position.fromAlgebraic("d2"), Position.fromAlgebraic("d4"));
        System.out.println("Move successful: " + result);

        System.out.println("\nBlack's turn - moving pawn a7-a6:");
        result = game.makeMove(Position.fromAlgebraic("a7"), Position.fromAlgebraic("a6"));
        System.out.println("Move successful: " + result);

        game.displayBoard();

        System.out.println("\nCurrent turn: " + game.getCurrentTurn());
        System.out.println("Current player: " + game.getCurrentPlayer());
        System.out.println("Game state: " + game.getGameState());

        System.out.println("\n=== Demo Complete ===");
    }
}
