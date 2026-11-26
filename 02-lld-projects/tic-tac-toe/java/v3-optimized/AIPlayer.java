import java.util.ArrayList;
import java.util.List;

/**
 * AI Player with Alpha-Beta Pruning optimization.
 * Significantly faster than basic minimax for larger boards.
 */
public class AIPlayer extends Player {
    private final Mark opponentMark;
    private int nodesEvaluated;

    public AIPlayer(String name, Mark mark) {
        super(name, mark);
        this.opponentMark = (mark == Mark.X) ? Mark.O : Mark.X;
    }

    @Override
    public Position makeMove(Board board) {
        System.out.println(getName() + " is thinking...");
        nodesEvaluated = 0;
        
        int bestScore = Integer.MIN_VALUE;
        Position bestMove = null;
        int alpha = Integer.MIN_VALUE;
        int beta = Integer.MAX_VALUE;
        
        List<Position> availableMoves = getOrderedMoves(board);
        
        for (Position move : availableMoves) {
            board.placeMark(move, getMark());
            int score = alphaBeta(board, 0, alpha, beta, false);
            board.removeMark(move);
            
            if (score > bestScore) {
                bestScore = score;
                bestMove = move;
            }
            alpha = Math.max(alpha, score);
        }
        
        System.out.println("  Evaluated " + nodesEvaluated + " positions");
        return bestMove;
    }

    /**
     * Minimax with Alpha-Beta Pruning.
     */
    private int alphaBeta(Board board, int depth, int alpha, int beta, boolean isMaximizing) {
        nodesEvaluated++;
        
        // Terminal state checks
        if (checkWin(board, getMark())) {
            return 100 - depth;
        }
        if (checkWin(board, opponentMark)) {
            return depth - 100;
        }
        if (board.isFull()) {
            return 0;
        }
        
        // Depth limit for larger boards
        int maxDepth = board.getSize() <= 3 ? 9 : 6;
        if (depth >= maxDepth) {
            return evaluateBoard(board);
        }
        
        List<Position> availableMoves = getOrderedMoves(board);
        
        if (isMaximizing) {
            int bestScore = Integer.MIN_VALUE;
            for (Position move : availableMoves) {
                board.placeMark(move, getMark());
                int score = alphaBeta(board, depth + 1, alpha, beta, false);
                board.removeMark(move);
                
                bestScore = Math.max(bestScore, score);
                alpha = Math.max(alpha, score);
                
                // Alpha-Beta pruning
                if (beta <= alpha) {
                    break;
                }
            }
            return bestScore;
        } else {
            int bestScore = Integer.MAX_VALUE;
            for (Position move : availableMoves) {
                board.placeMark(move, opponentMark);
                int score = alphaBeta(board, depth + 1, alpha, beta, true);
                board.removeMark(move);
                
                bestScore = Math.min(bestScore, score);
                beta = Math.min(beta, score);
                
                // Alpha-Beta pruning
                if (beta <= alpha) {
                    break;
                }
            }
            return bestScore;
        }
    }

    /**
     * Get moves ordered by priority (center, corners, edges).
     * Better move ordering improves alpha-beta pruning efficiency.
     */
    private List<Position> getOrderedMoves(Board board) {
        List<Position> centerMoves = new ArrayList<>();
        List<Position> cornerMoves = new ArrayList<>();
        List<Position> edgeMoves = new ArrayList<>();
        
        int size = board.getSize();
        int center = size / 2;
        
        for (int i = 0; i < size; i++) {
            for (int j = 0; j < size; j++) {
                Position pos = new Position(i, j);
                if (!board.isEmpty(pos)) {
                    continue;
                }
                
                // Center positions
                if (i == center && j == center) {
                    centerMoves.add(pos);
                }
                // Corner positions
                else if ((i == 0 || i == size - 1) && (j == 0 || j == size - 1)) {
                    cornerMoves.add(pos);
                }
                // Edge positions
                else {
                    edgeMoves.add(pos);
                }
            }
        }
        
        // Combine in priority order
        List<Position> orderedMoves = new ArrayList<>();
        orderedMoves.addAll(centerMoves);
        orderedMoves.addAll(cornerMoves);
        orderedMoves.addAll(edgeMoves);
        
        return orderedMoves;
    }

    /**
     * Heuristic evaluation for non-terminal states.
     */
    private int evaluateBoard(Board board) {
        int score = 0;
        int size = board.getSize();
        
        // Evaluate all lines
        for (int i = 0; i < size; i++) {
            score += evaluateLine(board, i, 0, 0, 1); // Row
            score += evaluateLine(board, 0, i, 1, 0); // Column
        }
        score += evaluateLine(board, 0, 0, 1, 1); // Main diagonal
        score += evaluateLine(board, 0, size - 1, 1, -1); // Anti diagonal
        
        return score;
    }

    /**
     * Evaluate a line for heuristic scoring.
     */
    private int evaluateLine(Board board, int startRow, int startCol, int rowDelta, int colDelta) {
        int myCount = 0;
        int oppCount = 0;
        int size = board.getSize();
        
        for (int i = 0; i < size; i++) {
            Position pos = new Position(startRow + i * rowDelta, startCol + i * colDelta);
            Mark mark = board.getMark(pos);
            
            if (mark == getMark()) {
                myCount++;
            } else if (mark == opponentMark) {
                oppCount++;
            }
        }
        
        // If line has both marks, no one can win on it
        if (myCount > 0 && oppCount > 0) {
            return 0;
        }
        
        // Score based on how many marks in the line
        if (myCount > 0) {
            return (int) Math.pow(10, myCount - 1);
        } else if (oppCount > 0) {
            return -(int) Math.pow(10, oppCount - 1);
        }
        
        return 0;
    }

    /**
     * Check if given mark has won.
     */
    private boolean checkWin(Board board, Mark mark) {
        int size = board.getSize();
        
        for (int i = 0; i < size; i++) {
            if (checkLine(board, mark, i, 0, 0, 1) ||
                checkLine(board, mark, 0, i, 1, 0)) {
                return true;
            }
        }
        
        return checkLine(board, mark, 0, 0, 1, 1) ||
               checkLine(board, mark, 0, size - 1, 1, -1);
    }

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
