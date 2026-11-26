/**
 * Represents the Tic-Tac-Toe game board.
 */
public class Board {
    public static final int DEFAULT_SIZE = 3;
    
    private final int size;
    private final Mark[][] cells;
    private int emptyCells;

    public Board() {
        this(DEFAULT_SIZE);
    }

    public Board(int size) {
        if (size < 1) {
            throw new IllegalArgumentException("Board size must be at least 1");
        }
        this.size = size;
        this.cells = new Mark[size][size];
        reset();
    }

    /**
     * Place a mark on the board.
     * 
     * @param position Position to place the mark
     * @param mark Mark to place
     * @return true if successful, false if invalid
     */
    public boolean placeMark(Position position, Mark mark) {
        if (!isValidMove(position)) {
            return false;
        }
        cells[position.getRow()][position.getCol()] = mark;
        emptyCells--;
        return true;
    }

    /**
     * Remove a mark from the board (for undo).
     */
    public void removeMark(Position position) {
        if (position.isValid(size) && cells[position.getRow()][position.getCol()] != Mark.EMPTY) {
            cells[position.getRow()][position.getCol()] = Mark.EMPTY;
            emptyCells++;
        }
    }

    /**
     * Get the mark at a position.
     */
    public Mark getMark(Position position) {
        if (!position.isValid(size)) {
            throw new IllegalArgumentException("Invalid position: " + position);
        }
        return cells[position.getRow()][position.getCol()];
    }

    /**
     * Check if a position is empty.
     */
    public boolean isEmpty(Position position) {
        return position.isValid(size) && cells[position.getRow()][position.getCol()] == Mark.EMPTY;
    }

    /**
     * Check if a move is valid.
     */
    public boolean isValidMove(Position position) {
        return position != null && position.isValid(size) && isEmpty(position);
    }

    /**
     * Check if the board is full.
     */
    public boolean isFull() {
        return emptyCells == 0;
    }

    /**
     * Get the board size.
     */
    public int getSize() {
        return size;
    }

    /**
     * Get count of empty cells.
     */
    public int getEmptyCells() {
        return emptyCells;
    }

    /**
     * Reset the board to initial state.
     */
    public void reset() {
        for (int i = 0; i < size; i++) {
            for (int j = 0; j < size; j++) {
                cells[i][j] = Mark.EMPTY;
            }
        }
        emptyCells = size * size;
    }

    /**
     * Display the board.
     */
    public void display() {
        StringBuilder sb = new StringBuilder();
        sb.append("\n");
        
        for (int i = 0; i < size; i++) {
            sb.append("  ");
            for (int j = 0; j < size; j++) {
                Mark mark = cells[i][j];
                if (mark == Mark.EMPTY) {
                    // Show position number (1-indexed)
                    sb.append(i * size + j + 1);
                } else {
                    sb.append(mark.getSymbol());
                }
                if (j < size - 1) {
                    sb.append(" | ");
                }
            }
            sb.append("\n");
            if (i < size - 1) {
                sb.append(" ");
                for (int j = 0; j < size; j++) {
                    sb.append("---");
                    if (j < size - 1) {
                        sb.append("+");
                    }
                }
                sb.append("\n");
            }
        }
        System.out.println(sb.toString());
    }

    /**
     * Get internal cells (for win checking).
     */
    Mark[][] getCells() {
        return cells;
    }
}
