/**
 * Represents a mark on the Tic-Tac-Toe board.
 */
public enum Mark {
    X('X'),
    O('O'),
    EMPTY(' ');

    private final char symbol;

    Mark(char symbol) {
        this.symbol = symbol;
    }

    public char getSymbol() {
        return symbol;
    }

    @Override
    public String toString() {
        return String.valueOf(symbol);
    }
}
