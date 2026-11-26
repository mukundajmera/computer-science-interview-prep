/**
 * Chess Game - V1 Basic
 * 
 * Position on the chess board.
 */
public class Position {
    private final int row;  // 0-7 (rank 1-8)
    private final int col;  // 0-7 (file a-h)

    public Position(int row, int col) {
        this.row = row;
        this.col = col;
    }

    public int getRow() {
        return row;
    }

    public int getCol() {
        return col;
    }

    public boolean isValid() {
        return row >= 0 && row < 8 && col >= 0 && col < 8;
    }

    /**
     * Convert to algebraic notation (e.g., "e4")
     */
    public String toAlgebraic() {
        char file = (char) ('a' + col);
        int rank = row + 1;
        return "" + file + rank;
    }

    /**
     * Create position from algebraic notation.
     */
    public static Position fromAlgebraic(String notation) {
        if (notation == null || notation.length() != 2) {
            throw new IllegalArgumentException("Invalid notation: " + notation);
        }
        char file = notation.charAt(0);
        char rank = notation.charAt(1);
        
        int col = file - 'a';
        int row = rank - '1';
        
        Position pos = new Position(row, col);
        if (!pos.isValid()) {
            throw new IllegalArgumentException("Invalid position: " + notation);
        }
        return pos;
    }

    @Override
    public boolean equals(Object obj) {
        if (this == obj) return true;
        if (obj == null || getClass() != obj.getClass()) return false;
        Position other = (Position) obj;
        return row == other.row && col == other.col;
    }

    @Override
    public int hashCode() {
        return 31 * row + col;
    }

    @Override
    public String toString() {
        return toAlgebraic();
    }
}

/**
 * Enumeration for piece colors.
 */
enum Color {
    WHITE, BLACK;

    public Color opposite() {
        return this == WHITE ? BLACK : WHITE;
    }
}

/**
 * Enumeration for game states.
 */
enum GameState {
    ACTIVE,
    CHECK,
    CHECKMATE,
    STALEMATE,
    RESIGNED
}
