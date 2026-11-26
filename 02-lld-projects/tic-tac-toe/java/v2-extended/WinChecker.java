/**
 * Checks for win conditions on the board.
 */
public class WinChecker {
    
    /**
     * Check if the last move resulted in a win.
     * 
     * @param board The game board
     * @param lastMove The last move made
     * @return true if the player who made the move won
     */
    public boolean checkWin(Board board, Position lastMove) {
        if (lastMove == null) {
            return false;
        }
        
        Mark mark = board.getMark(lastMove);
        if (mark == Mark.EMPTY) {
            return false;
        }
        
        int row = lastMove.getRow();
        int col = lastMove.getCol();
        int size = board.getSize();
        
        // Check row
        if (checkRow(board, row, mark)) {
            return true;
        }
        
        // Check column
        if (checkColumn(board, col, mark)) {
            return true;
        }
        
        // Check main diagonal (if applicable)
        if (row == col && checkMainDiagonal(board, mark)) {
            return true;
        }
        
        // Check anti-diagonal (if applicable)
        if (row + col == size - 1 && checkAntiDiagonal(board, mark)) {
            return true;
        }
        
        return false;
    }
    
    /**
     * Check if entire row has the same mark.
     */
    private boolean checkRow(Board board, int row, Mark mark) {
        int size = board.getSize();
        for (int col = 0; col < size; col++) {
            if (board.getMark(new Position(row, col)) != mark) {
                return false;
            }
        }
        return true;
    }
    
    /**
     * Check if entire column has the same mark.
     */
    private boolean checkColumn(Board board, int col, Mark mark) {
        int size = board.getSize();
        for (int row = 0; row < size; row++) {
            if (board.getMark(new Position(row, col)) != mark) {
                return false;
            }
        }
        return true;
    }
    
    /**
     * Check main diagonal (top-left to bottom-right).
     */
    private boolean checkMainDiagonal(Board board, Mark mark) {
        int size = board.getSize();
        for (int i = 0; i < size; i++) {
            if (board.getMark(new Position(i, i)) != mark) {
                return false;
            }
        }
        return true;
    }
    
    /**
     * Check anti-diagonal (top-right to bottom-left).
     */
    private boolean checkAntiDiagonal(Board board, Mark mark) {
        int size = board.getSize();
        for (int i = 0; i < size; i++) {
            if (board.getMark(new Position(i, size - 1 - i)) != mark) {
                return false;
            }
        }
        return true;
    }
}
