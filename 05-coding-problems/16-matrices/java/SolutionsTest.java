import java.util.*;

public class SolutionsTest {
    public static void main(String[] args) {
        Solutions sol = new Solutions();
        
        // test_isValidSudoku
        char[][] board1 = {
            {'5','3','.','.','7','.','.','.','.'},
            {'6','.','.','1','9','5','.','.','.'},
            {'.','9','8','.','.','.','.','6','.'},
            {'8','.','.','.','6','.','.','.','3'},
            {'4','.','.','8','.','3','.','.','1'},
            {'7','.','.','.','2','.','.','.','6'},
            {'.','6','.','.','.','.','2','8','.'},
            {'.','.','.','4','1','9','.','.','5'},
            {'.','.','.','.','8','.','.','7','9'}
        };
        assert sol.isValidSudoku(board1) : "test_isValidSudoku 1";
        
        char[][] board2 = {
            {'8','3','.','.','7','.','.','.','.'},
            {'6','.','.','1','9','5','.','.','.'},
            {'.','9','8','.','.','.','.','6','.'},
            {'8','.','.','.','6','.','.','.','3'},
            {'4','.','.','8','.','3','.','.','1'},
            {'7','.','.','.','2','.','.','.','6'},
            {'.','6','.','.','.','.','2','8','.'},
            {'.','.','.','4','1','9','.','.','5'},
            {'.','.','.','.','8','.','.','7','9'}
        };
        assert !sol.isValidSudoku(board2) : "test_isValidSudoku 2";
        
        char[][] board3 = new char[9][9];
        for (int i=0; i<9; i++) Arrays.fill(board3[i], '.');
        assert sol.isValidSudoku(board3) : "test_isValidSudoku 3";
        
        char[][] board4 = new char[9][9];
        for (int i=0; i<9; i++) Arrays.fill(board4[i], '.');
        board4[0][0] = '1';
        board4[1][8] = '1';
        assert sol.isValidSudoku(board4) : "test_isValidSudoku 4";
        
        char[][] board5 = new char[9][9];
        for (int i=0; i<9; i++) Arrays.fill(board5[i], '.');
        board5[0][0] = '2';
        board5[0][8] = '2';
        assert !sol.isValidSudoku(board5) : "test_isValidSudoku 5";
        
        char[][] board6 = new char[9][9];
        for (int i=0; i<9; i++) Arrays.fill(board6[i], '.');
        board6[0][0] = '3';
        board6[8][0] = '3';
        assert !sol.isValidSudoku(board6) : "test_isValidSudoku 6";

        // test_spiralOrder
        assert sol.spiralOrder(new int[][]{{1,2,3},{4,5,6},{7,8,9}}).equals(Arrays.asList(1,2,3,6,9,8,7,4,5)) : "test_spiralOrder 1";
        assert sol.spiralOrder(new int[][]{{1,2,3,4},{5,6,7,8},{9,10,11,12}}).equals(Arrays.asList(1,2,3,4,8,12,11,10,9,5,6,7)) : "test_spiralOrder 2";
        assert sol.spiralOrder(new int[][]{}).equals(Arrays.asList()) : "test_spiralOrder 3";
        assert sol.spiralOrder(new int[][]{{1}}).equals(Arrays.asList(1)) : "test_spiralOrder 4";
        assert sol.spiralOrder(new int[][]{{1,2},{3,4}}).equals(Arrays.asList(1,2,4,3)) : "test_spiralOrder 5";
        assert sol.spiralOrder(new int[][]{{1},{2},{3}}).equals(Arrays.asList(1,2,3)) : "test_spiralOrder 6";

        // test_rotate
        int[][] m1 = {{1,2,3},{4,5,6},{7,8,9}};
        sol.rotate(m1);
        assert Arrays.deepEquals(m1, new int[][]{{7,4,1},{8,5,2},{9,6,3}}) : "test_rotate 1";
        
        int[][] m2 = {{5,1,9,11},{2,4,8,10},{13,3,6,7},{15,14,12,16}};
        sol.rotate(m2);
        assert Arrays.deepEquals(m2, new int[][]{{15,13,2,5},{14,3,4,1},{12,6,8,9},{16,7,10,11}}) : "test_rotate 2";
        
        int[][] m3 = {{1}};
        sol.rotate(m3);
        assert Arrays.deepEquals(m3, new int[][]{{1}}) : "test_rotate 3";
        
        int[][] m4 = {{1,2},{3,4}};
        sol.rotate(m4);
        assert Arrays.deepEquals(m4, new int[][]{{3,1},{4,2}}) : "test_rotate 4";
        
        int[][] m5 = {{1,2,3,4,5},{6,7,8,9,10},{11,12,13,14,15},{16,17,18,19,20},{21,22,23,24,25}};
        sol.rotate(m5);
        assert Arrays.deepEquals(m5, new int[][]{{21,16,11,6,1},{22,17,12,7,2},{23,18,13,8,3},{24,19,14,9,4},{25,20,15,10,5}}) : "test_rotate 5";
        
        int[][] m6 = {{0,0},{0,0}};
        sol.rotate(m6);
        assert Arrays.deepEquals(m6, new int[][]{{0,0},{0,0}}) : "test_rotate 6";

        // test_setZeroes
        int[][] z1 = {{1,1,1},{1,0,1},{1,1,1}};
        sol.setZeroes(z1);
        assert Arrays.deepEquals(z1, new int[][]{{1,0,1},{0,0,0},{1,0,1}}) : "test_setZeroes 1";
        
        int[][] z2 = {{0,1,2,0},{3,4,5,2},{1,3,1,5}};
        sol.setZeroes(z2);
        assert Arrays.deepEquals(z2, new int[][]{{0,0,0,0},{0,4,5,0},{0,3,1,0}}) : "test_setZeroes 2";
        
        int[][] z3 = {{1}};
        sol.setZeroes(z3);
        assert Arrays.deepEquals(z3, new int[][]{{1}}) : "test_setZeroes 3";
        
        int[][] z4 = {{0}};
        sol.setZeroes(z4);
        assert Arrays.deepEquals(z4, new int[][]{{0}}) : "test_setZeroes 4";
        
        int[][] z5 = {{1,0}};
        sol.setZeroes(z5);
        assert Arrays.deepEquals(z5, new int[][]{{0,0}}) : "test_setZeroes 5";
        
        int[][] z6 = {{1,1},{1,1}};
        sol.setZeroes(z6);
        assert Arrays.deepEquals(z6, new int[][]{{1,1},{1,1}}) : "test_setZeroes 6";

        // test_gameOfLife
        int[][] g1 = {{0,1,0},{0,0,1},{1,1,1},{0,0,0}};
        sol.gameOfLife(g1);
        assert Arrays.deepEquals(g1, new int[][]{{0,0,0},{1,0,1},{0,1,1},{0,1,0}}) : "test_gameOfLife 1";
        
        int[][] g2 = {{1,1},{1,0}};
        sol.gameOfLife(g2);
        assert Arrays.deepEquals(g2, new int[][]{{1,1},{1,1}}) : "test_gameOfLife 2";
        
        int[][] g3 = {{0}};
        sol.gameOfLife(g3);
        assert Arrays.deepEquals(g3, new int[][]{{0}}) : "test_gameOfLife 3";
        
        int[][] g4 = {{1}};
        sol.gameOfLife(g4);
        assert Arrays.deepEquals(g4, new int[][]{{0}}) : "test_gameOfLife 4";
        
        int[][] g5 = {{1,1},{1,1}};
        sol.gameOfLife(g5);
        assert Arrays.deepEquals(g5, new int[][]{{1,1},{1,1}}) : "test_gameOfLife 5";
        
        int[][] g6 = {{0,0},{0,0}};
        sol.gameOfLife(g6);
        assert Arrays.deepEquals(g6, new int[][]{{0,0},{0,0}}) : "test_gameOfLife 6";

        // test_searchMatrix
        int[][] s1 = {{1,3,5,7},{10,11,16,20},{23,30,34,60}};
        assert sol.searchMatrix(s1, 3) : "test_searchMatrix 1";
        assert !sol.searchMatrix(s1, 13) : "test_searchMatrix 2";
        assert sol.searchMatrix(s1, 60) : "test_searchMatrix 3";
        assert !sol.searchMatrix(s1, 61) : "test_searchMatrix 4";
        
        int[][] s2 = {{1}};
        assert sol.searchMatrix(s2, 1) : "test_searchMatrix 5";
        assert !sol.searchMatrix(s2, 0) : "test_searchMatrix 6";
        
        int[][] s3 = {{1,1}};
        assert sol.searchMatrix(s3, 1) : "test_searchMatrix 7";
        
        assert !sol.searchMatrix(new int[][]{}, 1) : "test_searchMatrix 8";

        System.out.println("All Java tests passed!");
    }
}
