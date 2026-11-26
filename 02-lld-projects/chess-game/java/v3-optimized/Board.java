/**
 * Chess Game - V1 Basic
 * 
 * Chess board representation.
 */
public class Board {
    private final Piece[][] squares;

    public Board() {
        squares = new Piece[8][8];
    }

    /**
     * Get piece at position.
     */
    public Piece getPiece(Position pos) {
        if (!pos.isValid()) {
            return null;
        }
        return squares[pos.getRow()][pos.getCol()];
    }

    /**
     * Set piece at position.
     */
    public void setPiece(Position pos, Piece piece) {
        if (pos.isValid()) {
            squares[pos.getRow()][pos.getCol()] = piece;
            if (piece != null) {
                piece.position = pos;
            }
        }
    }

    /**
     * Remove and return piece at position.
     */
    public Piece removePiece(Position pos) {
        Piece piece = getPiece(pos);
        if (piece != null) {
            squares[pos.getRow()][pos.getCol()] = null;
        }
        return piece;
    }

    /**
     * Move piece from source to destination.
     */
    public Piece movePiece(Position from, Position to) {
        Piece piece = removePiece(from);
        Piece captured = removePiece(to);
        setPiece(to, piece);
        if (piece != null) {
            piece.setPosition(to);
        }
        return captured;
    }

    /**
     * Find king of given color.
     */
    public Position findKing(Color color) {
        for (int row = 0; row < 8; row++) {
            for (int col = 0; col < 8; col++) {
                Piece piece = squares[row][col];
                if (piece instanceof King && piece.getColor() == color) {
                    return new Position(row, col);
                }
            }
        }
        return null;
    }

    /**
     * Setup initial chess position.
     */
    public void setupInitialPosition() {
        // Clear board
        for (int row = 0; row < 8; row++) {
            for (int col = 0; col < 8; col++) {
                squares[row][col] = null;
            }
        }

        // White pieces (row 0 and 1)
        setupBackRank(0, Color.WHITE);
        for (int col = 0; col < 8; col++) {
            setPiece(new Position(1, col), new Pawn(Color.WHITE, new Position(1, col)));
        }

        // Black pieces (row 7 and 6)
        setupBackRank(7, Color.BLACK);
        for (int col = 0; col < 8; col++) {
            setPiece(new Position(6, col), new Pawn(Color.BLACK, new Position(6, col)));
        }
    }

    private void setupBackRank(int row, Color color) {
        setPiece(new Position(row, 0), new Rook(color, new Position(row, 0)));
        setPiece(new Position(row, 1), new Knight(color, new Position(row, 1)));
        setPiece(new Position(row, 2), new Bishop(color, new Position(row, 2)));
        setPiece(new Position(row, 3), new Queen(color, new Position(row, 3)));
        setPiece(new Position(row, 4), new King(color, new Position(row, 4)));
        setPiece(new Position(row, 5), new Bishop(color, new Position(row, 5)));
        setPiece(new Position(row, 6), new Knight(color, new Position(row, 6)));
        setPiece(new Position(row, 7), new Rook(color, new Position(row, 7)));
    }

    /**
     * Display the board.
     */
    public void display() {
        System.out.println("  a b c d e f g h");
        System.out.println("  ----------------");
        for (int row = 7; row >= 0; row--) {
            System.out.print((row + 1) + "|");
            for (int col = 0; col < 8; col++) {
                Piece piece = squares[row][col];
                char symbol = piece != null ? piece.getSymbol() : '.';
                System.out.print(symbol + " ");
            }
            System.out.println("|" + (row + 1));
        }
        System.out.println("  ----------------");
        System.out.println("  a b c d e f g h");
    }

    /**
     * Create a copy of the board for move simulation.
     */
    public Board copy() {
        Board copy = new Board();
        for (int row = 0; row < 8; row++) {
            for (int col = 0; col < 8; col++) {
                Piece piece = squares[row][col];
                if (piece != null) {
                    Position pos = new Position(row, col);
                    // Create new piece of same type
                    Piece newPiece = createPieceCopy(piece, pos);
                    copy.setPiece(pos, newPiece);
                }
            }
        }
        return copy;
    }

    private Piece createPieceCopy(Piece original, Position pos) {
        if (original instanceof King) return new King(original.getColor(), pos);
        if (original instanceof Queen) return new Queen(original.getColor(), pos);
        if (original instanceof Rook) return new Rook(original.getColor(), pos);
        if (original instanceof Bishop) return new Bishop(original.getColor(), pos);
        if (original instanceof Knight) return new Knight(original.getColor(), pos);
        if (original instanceof Pawn) return new Pawn(original.getColor(), pos);
        return null;
    }
}
