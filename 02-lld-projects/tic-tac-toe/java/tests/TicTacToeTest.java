import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import static org.junit.jupiter.api.Assertions.*;

/**
 * Tests for Tic-Tac-Toe implementation.
 */
public class TicTacToeTest {

    private Board board;
    
    @BeforeEach
    void setUp() {
        board = new Board(3);
    }

    // ===== Board Tests =====
    
    @Test
    @DisplayName("Board should initialize with all empty cells")
    void testBoardInitialization() {
        assertEquals(9, board.getEmptyCells());
        for (int i = 0; i < 3; i++) {
            for (int j = 0; j < 3; j++) {
                assertEquals(Mark.EMPTY, board.getMark(new Position(i, j)));
            }
        }
    }

    @Test
    @DisplayName("Should place mark on empty cell")
    void testPlaceMark() {
        Position pos = new Position(0, 0);
        assertTrue(board.placeMark(pos, Mark.X));
        assertEquals(Mark.X, board.getMark(pos));
        assertEquals(8, board.getEmptyCells());
    }

    @Test
    @DisplayName("Should not place mark on occupied cell")
    void testPlaceMarkOnOccupied() {
        Position pos = new Position(0, 0);
        board.placeMark(pos, Mark.X);
        assertFalse(board.placeMark(pos, Mark.O));
        assertEquals(Mark.X, board.getMark(pos));
    }

    @Test
    @DisplayName("Should remove mark correctly")
    void testRemoveMark() {
        Position pos = new Position(1, 1);
        board.placeMark(pos, Mark.X);
        assertEquals(8, board.getEmptyCells());
        
        board.removeMark(pos);
        assertEquals(Mark.EMPTY, board.getMark(pos));
        assertEquals(9, board.getEmptyCells());
    }

    @Test
    @DisplayName("Board should detect when full")
    void testBoardFull() {
        assertFalse(board.isFull());
        
        // Fill the board
        for (int i = 0; i < 3; i++) {
            for (int j = 0; j < 3; j++) {
                board.placeMark(new Position(i, j), Mark.X);
            }
        }
        
        assertTrue(board.isFull());
    }

    // ===== Position Tests =====
    
    @Test
    @DisplayName("Position validity check")
    void testPositionValidity() {
        assertTrue(new Position(0, 0).isValid(3));
        assertTrue(new Position(2, 2).isValid(3));
        assertFalse(new Position(-1, 0).isValid(3));
        assertFalse(new Position(3, 0).isValid(3));
        assertFalse(new Position(0, 3).isValid(3));
    }

    @Test
    @DisplayName("Position equality")
    void testPositionEquality() {
        Position p1 = new Position(1, 2);
        Position p2 = new Position(1, 2);
        Position p3 = new Position(2, 1);
        
        assertEquals(p1, p2);
        assertNotEquals(p1, p3);
        assertEquals(p1.hashCode(), p2.hashCode());
    }

    // ===== WinChecker Tests =====
    
    @Test
    @DisplayName("Should detect row win")
    void testRowWin() {
        WinChecker checker = new WinChecker();
        
        board.placeMark(new Position(0, 0), Mark.X);
        board.placeMark(new Position(0, 1), Mark.X);
        Position winPos = new Position(0, 2);
        board.placeMark(winPos, Mark.X);
        
        assertTrue(checker.checkWin(board, winPos));
    }

    @Test
    @DisplayName("Should detect column win")
    void testColumnWin() {
        WinChecker checker = new WinChecker();
        
        board.placeMark(new Position(0, 1), Mark.O);
        board.placeMark(new Position(1, 1), Mark.O);
        Position winPos = new Position(2, 1);
        board.placeMark(winPos, Mark.O);
        
        assertTrue(checker.checkWin(board, winPos));
    }

    @Test
    @DisplayName("Should detect main diagonal win")
    void testMainDiagonalWin() {
        WinChecker checker = new WinChecker();
        
        board.placeMark(new Position(0, 0), Mark.X);
        board.placeMark(new Position(1, 1), Mark.X);
        Position winPos = new Position(2, 2);
        board.placeMark(winPos, Mark.X);
        
        assertTrue(checker.checkWin(board, winPos));
    }

    @Test
    @DisplayName("Should detect anti-diagonal win")
    void testAntiDiagonalWin() {
        WinChecker checker = new WinChecker();
        
        board.placeMark(new Position(0, 2), Mark.O);
        board.placeMark(new Position(1, 1), Mark.O);
        Position winPos = new Position(2, 0);
        board.placeMark(winPos, Mark.O);
        
        assertTrue(checker.checkWin(board, winPos));
    }

    @Test
    @DisplayName("Should not detect win when no winning line")
    void testNoWin() {
        WinChecker checker = new WinChecker();
        
        board.placeMark(new Position(0, 0), Mark.X);
        board.placeMark(new Position(0, 1), Mark.O);
        Position lastPos = new Position(0, 2);
        board.placeMark(lastPos, Mark.X);
        
        assertFalse(checker.checkWin(board, lastPos));
    }

    // ===== Game Tests =====
    
    @Test
    @DisplayName("Game should start correctly")
    void testGameStart() {
        TestPlayer p1 = new TestPlayer("P1", Mark.X);
        TestPlayer p2 = new TestPlayer("P2", Mark.O);
        Game game = new Game(p1, p2);
        
        assertEquals(GameState.NOT_STARTED, game.getState());
        game.start();
        assertEquals(GameState.IN_PROGRESS, game.getState());
    }

    @Test
    @DisplayName("Game should alternate players")
    void testPlayerAlternation() {
        TestPlayer p1 = new TestPlayer("P1", Mark.X);
        TestPlayer p2 = new TestPlayer("P2", Mark.O);
        Game game = new Game(p1, p2);
        game.start();
        
        assertEquals(p1, game.getCurrentPlayer());
        game.makeMove(new Position(0, 0));
        assertEquals(p2, game.getCurrentPlayer());
        game.makeMove(new Position(0, 1));
        assertEquals(p1, game.getCurrentPlayer());
    }

    @Test
    @DisplayName("Game should detect X win")
    void testXWin() {
        TestPlayer p1 = new TestPlayer("P1", Mark.X);
        TestPlayer p2 = new TestPlayer("P2", Mark.O);
        Game game = new Game(p1, p2);
        game.start();
        
        game.makeMove(new Position(0, 0)); // X
        game.makeMove(new Position(1, 0)); // O
        game.makeMove(new Position(0, 1)); // X
        game.makeMove(new Position(1, 1)); // O
        game.makeMove(new Position(0, 2)); // X wins
        
        assertEquals(GameState.X_WON, game.getState());
        assertTrue(game.isGameOver());
    }

    @Test
    @DisplayName("Game should detect O win")
    void testOWin() {
        TestPlayer p1 = new TestPlayer("P1", Mark.X);
        TestPlayer p2 = new TestPlayer("P2", Mark.O);
        Game game = new Game(p1, p2);
        game.start();
        
        game.makeMove(new Position(0, 0)); // X
        game.makeMove(new Position(1, 0)); // O
        game.makeMove(new Position(0, 1)); // X
        game.makeMove(new Position(1, 1)); // O
        game.makeMove(new Position(2, 2)); // X (not winning)
        game.makeMove(new Position(1, 2)); // O wins
        
        assertEquals(GameState.O_WON, game.getState());
    }

    @Test
    @DisplayName("Game should detect draw")
    void testDraw() {
        TestPlayer p1 = new TestPlayer("P1", Mark.X);
        TestPlayer p2 = new TestPlayer("P2", Mark.O);
        Game game = new Game(p1, p2);
        game.start();
        
        // Play a draw game:
        // X | O | X
        // X | X | O
        // O | X | O
        game.makeMove(new Position(0, 0)); // X
        game.makeMove(new Position(0, 1)); // O
        game.makeMove(new Position(0, 2)); // X
        game.makeMove(new Position(1, 2)); // O
        game.makeMove(new Position(1, 0)); // X
        game.makeMove(new Position(2, 0)); // O
        game.makeMove(new Position(1, 1)); // X
        game.makeMove(new Position(2, 2)); // O
        game.makeMove(new Position(2, 1)); // X
        
        assertEquals(GameState.DRAW, game.getState());
    }

    @Test
    @DisplayName("Should not allow moves after game over")
    void testNoMovesAfterGameOver() {
        TestPlayer p1 = new TestPlayer("P1", Mark.X);
        TestPlayer p2 = new TestPlayer("P2", Mark.O);
        Game game = new Game(p1, p2);
        game.start();
        
        // X wins
        game.makeMove(new Position(0, 0));
        game.makeMove(new Position(1, 0));
        game.makeMove(new Position(0, 1));
        game.makeMove(new Position(1, 1));
        game.makeMove(new Position(0, 2));
        
        // Try to make another move
        assertFalse(game.makeMove(new Position(2, 2)));
    }

    @Test
    @DisplayName("Game reset should work correctly")
    void testGameReset() {
        TestPlayer p1 = new TestPlayer("P1", Mark.X);
        TestPlayer p2 = new TestPlayer("P2", Mark.O);
        Game game = new Game(p1, p2);
        game.start();
        game.makeMove(new Position(0, 0));
        game.makeMove(new Position(0, 1));
        
        game.reset();
        
        assertEquals(GameState.NOT_STARTED, game.getState());
        assertEquals(9, game.getBoard().getEmptyCells());
    }

    // ===== N×N Board Tests =====
    
    @Test
    @DisplayName("Should work with 4x4 board")
    void test4x4Board() {
        Board board4 = new Board(4);
        assertEquals(16, board4.getEmptyCells());
        assertEquals(4, board4.getSize());
        
        WinChecker checker = new WinChecker();
        
        // Create a row win
        board4.placeMark(new Position(1, 0), Mark.X);
        board4.placeMark(new Position(1, 1), Mark.X);
        board4.placeMark(new Position(1, 2), Mark.X);
        Position winPos = new Position(1, 3);
        board4.placeMark(winPos, Mark.X);
        
        assertTrue(checker.checkWin(board4, winPos));
    }

    // ===== Helper Test Player =====
    
    static class TestPlayer extends Player {
        public TestPlayer(String name, Mark mark) {
            super(name, mark);
        }
        
        @Override
        public Position makeMove(Board board) {
            // Not used in these tests
            return null;
        }
    }
}
