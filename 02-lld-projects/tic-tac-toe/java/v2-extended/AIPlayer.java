import java.util.ArrayList;
import java.util.List;

/**
 * AI Player using Minimax algorithm.
 */
public class AIPlayer extends Player {
    private final Mark opponentMark;

    public AIPlayer(String name, Mark mark) {
        super(name, mark);
        this.opponentMark = (mark == Mark.X) ? Mark.O : Mark.X;
    }

    @Override
    public Position makeMove(Board board) {
        System.out.println(getName() + " is thinking...");
        
        int bestScore = Integer.MIN_VALUE;
        Position bestMove = null;
        
        List<Position> availableMoves = getAvailableMoves(board);
        
        for (Position move : availableMoves) {
            // Make the move
            board.placeMark(move, getMark());
            
            // Calculate score using minimax
            int score = minimax(board, 0, false);
            
            // Undo the move
            board.removeMark(move);
            
            if (score > bestScore) {
                bestScore = score;
                bestMove = move;
            }
        }
        
        return bestMove;
    }

    /**
     * Minimax algorithm to find optimal move.
     */
    private int minimax(Board board, int depth, boolean isMaximizing) {
        // Check terminal states
        if (checkWin(board, getMark())) {
            return 10 - depth; // AI wins (prefer quicker wins)
        }
        if (checkWin(board, opponentMark)) {
            return depth - 10; // Opponent wins (prefer slower losses)
        }
        if (board.isFull()) {
            return 0; // Draw
        }
        
        List<Position> availableMoves = getAvailableMoves(board);
        
        if (isMaximizing) {
            int bestScore = Integer.MIN_VALUE;
            for (Position move : availableMoves) {
                board.placeMark(move, getMark());
                int score = minimax(board, depth + 1, false);
                board.removeMark(move);
                bestScore = Math.max(bestScore, score);
            }
            return bestScore;
        } else {
            int bestScore = Integer.MAX_VALUE;
            for (Position move : availableMoves) {
                board.placeMark(move, opponentMark);
                int score = minimax(board, depth + 1, true);
                board.removeMark(move);
                bestScore = Math.min(bestScore, score);
            }
            return bestScore;
        }
    }

    /**
     * Get all available moves on the board.
     */
    private List<Position> getAvailableMoves(Board board) {
        List<Position> moves = new ArrayList<>();
        int size = board.getSize();
        
        for (int i = 0; i < size; i++) {
            for (int j = 0; j < size; j++) {
                Position pos = new Position(i, j);
                if (board.isEmpty(pos)) {
                    moves.add(pos);
                }
            }
        }
        return moves;
    }

    /**
     * Check if given mark has won.
     */
    private boolean checkWin(Board board, Mark mark) {
        int size = board.getSize();
        
        // Check rows and columns
        for (int i = 0; i < size; i++) {
            if (checkLine(board, mark, i, 0, 0, 1) || // Row
                checkLine(board, mark, 0, i, 1, 0)) { // Column
                return true;
            }
        }
        
        // Check diagonals
        return checkLine(board, mark, 0, 0, 1, 1) || // Main diagonal
               checkLine(board, mark, 0, size - 1, 1, -1); // Anti diagonal
    }

    /**
     * Check if a line has all same marks.
     */
    private boolean checkLine(Board board, Mark mark, int startRow, int startCol, int rowDelta, int colDelta) {
        int size = board.getSize();
        for (int i = 0; i < size; i++) {
            Position pos = new Position(startRow + i * rowDelta, startCol + i * colDelta);
            if (board.getMark(pos) != mark) {
                return false;
            }
        }
        return true;
    }
}
