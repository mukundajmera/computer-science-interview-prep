import java.util.ArrayList;
import java.util.List;

/**
 * Chess Game - V2 Extended
 * 
 * Move class with command pattern for undo support.
 */
public class Move {
    private final Piece piece;
    private final Position from;
    private final Position to;
    private final Piece capturedPiece;
    private final boolean isFirstMove;
    private final MoveType type;

    public enum MoveType {
        NORMAL, CAPTURE, CASTLING_KINGSIDE, CASTLING_QUEENSIDE, EN_PASSANT, PROMOTION
    }

    public Move(Piece piece, Position from, Position to, Piece capturedPiece, MoveType type, boolean isFirstMove) {
        this.piece = piece;
        this.from = from;
        this.to = to;
        this.capturedPiece = capturedPiece;
        this.type = type;
        this.isFirstMove = isFirstMove;
    }

    public Piece getPiece() { return piece; }
    public Position getFrom() { return from; }
    public Position getTo() { return to; }
    public Piece getCapturedPiece() { return capturedPiece; }
    public MoveType getType() { return type; }

    /**
     * Execute the move on the board.
     */
    public void execute(Board board) {
        board.movePiece(from, to);
    }

    /**
     * Undo the move on the board.
     */
    public void undo(Board board) {
        // Move piece back
        board.movePiece(to, from);
        
        // Restore captured piece
        if (capturedPiece != null) {
            board.setPiece(to, capturedPiece);
        }
        
        // Restore first move flag
        if (isFirstMove) {
            piece.hasMoved = false;
        }
    }

    /**
     * Convert to algebraic notation.
     */
    public String toAlgebraic() {
        StringBuilder sb = new StringBuilder();
        
        if (type == MoveType.CASTLING_KINGSIDE) {
            return "O-O";
        } else if (type == MoveType.CASTLING_QUEENSIDE) {
            return "O-O-O";
        }
        
        // Piece symbol (except pawn)
        if (!(piece instanceof Pawn)) {
            sb.append(Character.toUpperCase(piece.getSymbol()));
        }
        
        // Capture notation
        if (capturedPiece != null) {
            if (piece instanceof Pawn) {
                sb.append((char) ('a' + from.getCol()));
            }
            sb.append("x");
        }
        
        sb.append(to.toAlgebraic());
        
        return sb.toString();
    }

    @Override
    public String toString() {
        return toAlgebraic();
    }
}

// Import statements would be at top in real file
// Using same Position, Color, GameState, Board, Piece classes from v1
// Extended with move history support
