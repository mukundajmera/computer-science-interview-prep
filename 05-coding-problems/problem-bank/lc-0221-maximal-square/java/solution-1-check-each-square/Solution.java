class Solution {
    public int maximalSquare(char[][] matrix) {
        int rows = matrix.length;
        int cols = matrix[0].length;
        int bestSide = 0;

        for (int row = 0; row < rows; row++) {
            for (int col = 0; col < cols; col++) {
                int maxSide = Math.min(rows - row, cols - col);
                for (int side = 1; side <= maxSide; side++) {
                    if (isAllOnes(matrix, row, col, side)) {
                        bestSide = Math.max(bestSide, side);
                    } else {
                        break;
                    }
                }
            }
        }

        return bestSide * bestSide;
    }

    private boolean isAllOnes(char[][] matrix, int top, int left, int side) {
        for (int row = top; row < top + side; row++) {
            for (int col = left; col < left + side; col++) {
                if (matrix[row][col] != '1') {
                    return false;
                }
            }
        }
        return true;
    }
}
