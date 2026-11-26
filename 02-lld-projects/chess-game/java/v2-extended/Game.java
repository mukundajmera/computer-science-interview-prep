import java.util.List;

/**
 * Chess Game - V1 Basic
 * 
 * Main game controller.
 */
public class Game {
    private final Board board;
    private final Player whitePlayer;
    private final Player blackPlayer;
    private Color currentTurn;
    private GameState gameState;

    public Game(String whiteName, String blackName) {
        this.board = new Board();
        this.whitePlayer = new Player(whiteName, Color.WHITE);
        this.blackPlayer = new Player(blackName, Color.BLACK);
        this.currentTurn = Color.WHITE;
        this.gameState = GameState.ACTIVE;
        
        board.setupInitialPosition();
    }

    /**
     * Make a move from source to destination.
     * 
     * @return true if move was successful, false otherwise
     */
    public boolean makeMove(Position from, Position to) {
        // Validate basic conditions
        if (gameState == GameState.CHECKMATE || gameState == GameState.STALEMATE) {
            System.out.println("Game is over!");
            return false;
        }

        Piece piece = board.getPiece(from);

        // Check if there's a piece at source
        if (piece == null) {
            System.out.println("No piece at " + from);
            return false;
        }

        // Check if it's the right player's turn
        if (piece.getColor() != currentTurn) {
            System.out.println("It's " + currentTurn + "'s turn!");
            return false;
        }

        // Check if move is valid for this piece
        List<Position> validMoves = piece.getValidMoves(board);
        if (!validMoves.contains(to)) {
            System.out.println("Invalid move for " + piece.getClass().getSimpleName());
            return false;
        }

        // Execute the move
        Piece captured = board.movePiece(from, to);

        if (captured != null) {
            System.out.println("Captured " + captured);
        }

        // Switch turns
        currentTurn = currentTurn.opposite();

        return true;
    }

    /**
     * Get valid moves for piece at position.
     */
    public List<Position> getValidMoves(Position pos) {
        Piece piece = board.getPiece(pos);
        if (piece == null) {
            return List.of();
        }
        return piece.getValidMoves(board);
    }

    /**
     * Get the current player.
     */
    public Player getCurrentPlayer() {
        return currentTurn == Color.WHITE ? whitePlayer : blackPlayer;
    }

    /**
     * Get current turn color.
     */
    public Color getCurrentTurn() {
        return currentTurn;
    }

    /**
     * Get game state.
     */
    public GameState getGameState() {
        return gameState;
    }

    /**
     * Get the board.
     */
    public Board getBoard() {
        return board;
    }

    /**
     * Display the board.
     */
    public void displayBoard() {
        board.display();
    }

    /**
     * Resign the current player.
     */
    public void resign() {
        gameState = GameState.RESIGNED;
        System.out.println(getCurrentPlayer().getName() + " resigned!");
        System.out.println(currentTurn.opposite() + " wins!");
    }
}

/**
 * Player representation.
 */
class Player {
    private final String name;
    private final Color color;

    public Player(String name, Color color) {
        this.name = name;
        this.color = color;
    }

    public String getName() {
        return name;
    }

    public Color getColor() {
        return color;
    }

    @Override
    public String toString() {
        return String.format("%s (%s)", name, color);
    }
}
