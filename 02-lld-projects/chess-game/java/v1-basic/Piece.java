import java.util.ArrayList;
import java.util.List;

/**
 * Chess Game - V1 Basic
 * 
 * Abstract base class for all chess pieces.
 */
public abstract class Piece {
    protected Color color;
    protected Position position;
    protected boolean hasMoved;

    public Piece(Color color, Position position) {
        this.color = color;
        this.position = position;
        this.hasMoved = false;
    }

    public Color getColor() {
        return color;
    }

    public Position getPosition() {
        return position;
    }

    public void setPosition(Position position) {
        this.position = position;
        this.hasMoved = true;
    }

    public boolean hasMoved() {
        return hasMoved;
    }

    /**
     * Get all valid move destinations from current position.
     */
    public abstract List<Position> getValidMoves(Board board);

    /**
     * Check if this piece can move to target position.
     */
    public boolean canMoveTo(Board board, Position target) {
        return getValidMoves(board).contains(target);
    }

    /**
     * Get the symbol for this piece (for display).
     */
    public abstract char getSymbol();

    /**
     * Check if target position is valid and either empty or has opponent's piece.
     */
    protected boolean isValidTarget(Board board, Position target) {
        if (!target.isValid()) {
            return false;
        }
        Piece pieceAtTarget = board.getPiece(target);
        return pieceAtTarget == null || pieceAtTarget.getColor() != this.color;
    }

    @Override
    public String toString() {
        return String.format("%s%s@%s", color, getClass().getSimpleName(), position);
    }
}

/**
 * King - moves one square in any direction.
 */
class King extends Piece {
    private static final int[][] DIRECTIONS = {
        {-1, -1}, {-1, 0}, {-1, 1},
        {0, -1},          {0, 1},
        {1, -1}, {1, 0}, {1, 1}
    };

    public King(Color color, Position position) {
        super(color, position);
    }

    @Override
    public List<Position> getValidMoves(Board board) {
        List<Position> moves = new ArrayList<>();
        for (int[] dir : DIRECTIONS) {
            Position target = new Position(position.getRow() + dir[0], position.getCol() + dir[1]);
            if (isValidTarget(board, target)) {
                moves.add(target);
            }
        }
        return moves;
    }

    @Override
    public char getSymbol() {
        return color == Color.WHITE ? 'K' : 'k';
    }
}

/**
 * Queen - moves any number of squares in any direction.
 */
class Queen extends Piece {
    private static final int[][] DIRECTIONS = {
        {-1, -1}, {-1, 0}, {-1, 1},
        {0, -1},          {0, 1},
        {1, -1}, {1, 0}, {1, 1}
    };

    public Queen(Color color, Position position) {
        super(color, position);
    }

    @Override
    public List<Position> getValidMoves(Board board) {
        List<Position> moves = new ArrayList<>();
        for (int[] dir : DIRECTIONS) {
            addMovesInDirection(board, moves, dir[0], dir[1]);
        }
        return moves;
    }

    private void addMovesInDirection(Board board, List<Position> moves, int rowDir, int colDir) {
        int row = position.getRow() + rowDir;
        int col = position.getCol() + colDir;
        
        while (row >= 0 && row < 8 && col >= 0 && col < 8) {
            Position target = new Position(row, col);
            Piece pieceAtTarget = board.getPiece(target);
            
            if (pieceAtTarget == null) {
                moves.add(target);
            } else {
                if (pieceAtTarget.getColor() != this.color) {
                    moves.add(target);  // Can capture
                }
                break;  // Blocked
            }
            row += rowDir;
            col += colDir;
        }
    }

    @Override
    public char getSymbol() {
        return color == Color.WHITE ? 'Q' : 'q';
    }
}

/**
 * Rook - moves any number of squares horizontally or vertically.
 */
class Rook extends Piece {
    private static final int[][] DIRECTIONS = {
        {-1, 0}, {1, 0}, {0, -1}, {0, 1}
    };

    public Rook(Color color, Position position) {
        super(color, position);
    }

    @Override
    public List<Position> getValidMoves(Board board) {
        List<Position> moves = new ArrayList<>();
        for (int[] dir : DIRECTIONS) {
            addMovesInDirection(board, moves, dir[0], dir[1]);
        }
        return moves;
    }

    private void addMovesInDirection(Board board, List<Position> moves, int rowDir, int colDir) {
        int row = position.getRow() + rowDir;
        int col = position.getCol() + colDir;
        
        while (row >= 0 && row < 8 && col >= 0 && col < 8) {
            Position target = new Position(row, col);
            Piece pieceAtTarget = board.getPiece(target);
            
            if (pieceAtTarget == null) {
                moves.add(target);
            } else {
                if (pieceAtTarget.getColor() != this.color) {
                    moves.add(target);
                }
                break;
            }
            row += rowDir;
            col += colDir;
        }
    }

    @Override
    public char getSymbol() {
        return color == Color.WHITE ? 'R' : 'r';
    }
}

/**
 * Bishop - moves any number of squares diagonally.
 */
class Bishop extends Piece {
    private static final int[][] DIRECTIONS = {
        {-1, -1}, {-1, 1}, {1, -1}, {1, 1}
    };

    public Bishop(Color color, Position position) {
        super(color, position);
    }

    @Override
    public List<Position> getValidMoves(Board board) {
        List<Position> moves = new ArrayList<>();
        for (int[] dir : DIRECTIONS) {
            addMovesInDirection(board, moves, dir[0], dir[1]);
        }
        return moves;
    }

    private void addMovesInDirection(Board board, List<Position> moves, int rowDir, int colDir) {
        int row = position.getRow() + rowDir;
        int col = position.getCol() + colDir;
        
        while (row >= 0 && row < 8 && col >= 0 && col < 8) {
            Position target = new Position(row, col);
            Piece pieceAtTarget = board.getPiece(target);
            
            if (pieceAtTarget == null) {
                moves.add(target);
            } else {
                if (pieceAtTarget.getColor() != this.color) {
                    moves.add(target);
                }
                break;
            }
            row += rowDir;
            col += colDir;
        }
    }

    @Override
    public char getSymbol() {
        return color == Color.WHITE ? 'B' : 'b';
    }
}

/**
 * Knight - moves in L-shape (2+1), can jump over pieces.
 */
class Knight extends Piece {
    private static final int[][] MOVES = {
        {-2, -1}, {-2, 1}, {-1, -2}, {-1, 2},
        {1, -2}, {1, 2}, {2, -1}, {2, 1}
    };

    public Knight(Color color, Position position) {
        super(color, position);
    }

    @Override
    public List<Position> getValidMoves(Board board) {
        List<Position> moves = new ArrayList<>();
        for (int[] move : MOVES) {
            Position target = new Position(position.getRow() + move[0], position.getCol() + move[1]);
            if (isValidTarget(board, target)) {
                moves.add(target);
            }
        }
        return moves;
    }

    @Override
    public char getSymbol() {
        return color == Color.WHITE ? 'N' : 'n';
    }
}

/**
 * Pawn - moves forward, captures diagonally.
 */
class Pawn extends Piece {
    public Pawn(Color color, Position position) {
        super(color, position);
    }

    @Override
    public List<Position> getValidMoves(Board board) {
        List<Position> moves = new ArrayList<>();
        int direction = (color == Color.WHITE) ? 1 : -1;
        int startRow = (color == Color.WHITE) ? 1 : 6;

        // Forward move
        Position oneForward = new Position(position.getRow() + direction, position.getCol());
        if (oneForward.isValid() && board.getPiece(oneForward) == null) {
            moves.add(oneForward);

            // Double move from starting position
            if (position.getRow() == startRow) {
                Position twoForward = new Position(position.getRow() + 2 * direction, position.getCol());
                if (board.getPiece(twoForward) == null) {
                    moves.add(twoForward);
                }
            }
        }

        // Diagonal captures
        for (int colOffset : new int[]{-1, 1}) {
            Position capturePos = new Position(position.getRow() + direction, position.getCol() + colOffset);
            if (capturePos.isValid()) {
                Piece targetPiece = board.getPiece(capturePos);
                if (targetPiece != null && targetPiece.getColor() != this.color) {
                    moves.add(capturePos);
                }
            }
        }

        return moves;
    }

    @Override
    public char getSymbol() {
        return color == Color.WHITE ? 'P' : 'p';
    }
}
