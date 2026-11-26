public class Board {
    private final int rows;
    private final int cols;
    private final DiscColor[][] grid;

    public Board() {
        this(6, 7);
    }

    public Board(int rows, int cols) {
        if (rows < 4 || cols < 4) {
            throw new IllegalArgumentException("Board must be at least 4x4");
        }
        this.rows = rows;
        this.cols = cols;
        this.grid = new DiscColor[rows][cols];
        for (int r = 0; r < rows; r++) {
            for (int c = 0; c < cols; c++) {
                grid[r][c] = DiscColor.EMPTY;
            }
        }
    }

    public int getRows() {
        return rows;
    }

    public int getCols() {
        return cols;
    }

    public DiscColor getCell(int row, int col) {
        if (!isInBounds(row, col)) {
            throw new IllegalArgumentException("Invalid cell");
        }
        return grid[row][col];
    }

    public boolean canPlace(int column) {
        if (column < 0 || column >= cols) {
            return false;
        }
        return grid[0][column] == DiscColor.EMPTY;
    }

    public int placeDisc(int column, DiscColor color) {
        if (!canPlace(column)) {
            return -1;
        }
        for (int row = rows - 1; row >= 0; row--) {
            if (grid[row][column] == DiscColor.EMPTY) {
                grid[row][column] = color;
                return row;
            }
        }
        return -1;
    }

    public void clearCell(int row, int col) {
        if (!isInBounds(row, col)) {
            throw new IllegalArgumentException("Invalid cell");
        }
        grid[row][col] = DiscColor.EMPTY;
    }

    public boolean isFull() {
        for (int col = 0; col < cols; col++) {
            if (canPlace(col)) {
                return false;
            }
        }
        return true;
    }

    public boolean checkWin(int row, int col, DiscColor color) {
        return countConnected(row, col, 0, 1, color) >= 4 ||
                countConnected(row, col, 1, 0, color) >= 4 ||
                countConnected(row, col, 1, 1, color) >= 4 ||
                countConnected(row, col, 1, -1, color) >= 4;
    }

    private int countConnected(int row, int col, int dr, int dc, DiscColor color) {
        int total = 1;
        total += countDirection(row, col, dr, dc, color);
        total += countDirection(row, col, -dr, -dc, color);
        return total;
    }

    private int countDirection(int row, int col, int dr, int dc, DiscColor color) {
        int count = 0;
        int r = row + dr;
        int c = col + dc;
        while (isInBounds(r, c) && grid[r][c] == color) {
            count++;
            r += dr;
            c += dc;
        }
        return count;
    }

    private boolean isInBounds(int row, int col) {
        return row >= 0 && row < rows && col >= 0 && col < cols;
    }
}
