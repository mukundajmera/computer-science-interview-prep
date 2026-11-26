import java.util.HashSet;
import java.util.Set;

class Solution {
    public boolean isValidSudoku(char[][] board) {
        for (int row = 0; row < 9; row++) {
            Set<Character> seen = new HashSet<>();
            for (int col = 0; col < 9; col++) {
                if (!addIfDigitIsNew(seen, board[row][col])) {
                    return false;
                }
            }
        }
        for (int col = 0; col < 9; col++) {
            Set<Character> seen = new HashSet<>();
            for (int row = 0; row < 9; row++) {
                if (!addIfDigitIsNew(seen, board[row][col])) {
                    return false;
                }
            }
        }
        for (int boxRow = 0; boxRow < 9; boxRow += 3) {
            for (int boxCol = 0; boxCol < 9; boxCol += 3) {
                Set<Character> seen = new HashSet<>();
                for (int row = boxRow; row < boxRow + 3; row++) {
                    for (int col = boxCol; col < boxCol + 3; col++) {
                        if (!addIfDigitIsNew(seen, board[row][col])) {
                            return false;
                        }
                    }
                }
            }
        }
        return true;
    }

    private boolean addIfDigitIsNew(Set<Character> seen, char value) {
        if (value == '.') {
            return true;
        }
        return seen.add(value);
    }
}
