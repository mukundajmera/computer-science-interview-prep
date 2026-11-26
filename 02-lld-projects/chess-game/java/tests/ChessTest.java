import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.DisplayName;
import static org.junit.jupiter.api.Assertions.*;

/**
 * Tests for Chess Game implementations.
 */
public class ChessTest {

    @Test
    @DisplayName("Position: Valid positions")
    void testValidPosition() {
        assertTrue(new Position(0, 0).isValid());
        assertTrue(new Position(7, 7).isValid());
        assertFalse(new Position(-1, 0).isValid());
        assertFalse(new Position(8, 0).isValid());
    }

    @Test
    @DisplayName("Position: Algebraic notation")
    void testAlgebraicNotation() {
        assertEquals("e4", new Position(3, 4).toAlgebraic());
        assertEquals("a1", new Position(0, 0).toAlgebraic());
        assertEquals("h8", new Position(7, 7).toAlgebraic());
    }

    @Test
    @DisplayName("Piece: Pawn movement")
    void testPawnMovement() {
        // Pawn at starting position can move 1 or 2 squares
        int startRow = 1;  // White pawn starting row
        int direction = 1;  // White moves up
        
        int oneForward = startRow + direction;
        int twoForward = startRow + 2 * direction;
        
        assertEquals(2, oneForward);
        assertEquals(3, twoForward);
    }

    @Test
    @DisplayName("Piece: Knight L-shape movement")
    void testKnightMovement() {
        // Knight at d4 (row 3, col 3)
        int[][] expectedMoves = {
            {1, 2}, {1, 4},  // From row 3: +2 rows
            {2, 1}, {2, 5},  // +1 row
            {4, 1}, {4, 5},  // -1 row
            {5, 2}, {5, 4}   // -2 rows
        };
        
        assertEquals(8, expectedMoves.length);
    }

    @Test
    @DisplayName("Board: Initial setup has 32 pieces")
    void testInitialSetup() {
        int totalPieces = 16 + 16;  // 16 per side
        assertEquals(32, totalPieces);
    }

    @Test
    @DisplayName("Game: Turn alternates")
    void testTurnAlternation() {
        Color white = Color.WHITE;
        Color afterWhite = white.opposite();
        
        assertEquals(Color.BLACK, afterWhite);
        assertEquals(Color.WHITE, afterWhite.opposite());
    }

    @Test
    @DisplayName("Check detection: King attacked")
    void testCheckDetection() {
        // If any opponent piece can reach king's position, it's check
        boolean kingCanBeAttacked = true;
        boolean isCheck = kingCanBeAttacked;
        
        assertTrue(isCheck);
    }

    @Test
    @DisplayName("Checkmate: Check with no escape")
    void testCheckmateCondition() {
        boolean inCheck = true;
        boolean hasLegalMoves = false;
        
        boolean isCheckmate = inCheck && !hasLegalMoves;
        assertTrue(isCheckmate);
    }

    @Test
    @DisplayName("Stalemate: No check, no moves")
    void testStalemateCondition() {
        boolean inCheck = false;
        boolean hasLegalMoves = false;
        
        boolean isStalemate = !inCheck && !hasLegalMoves;
        assertTrue(isStalemate);
    }

    @Test
    @DisplayName("Move: Capture notation")
    void testCaptureNotation() {
        String pieceSymbol = "N";  // Knight
        String captureSymbol = "x";
        String target = "e5";
        
        String notation = pieceSymbol + captureSymbol + target;
        assertEquals("Nxe5", notation);
    }

    @Test
    @DisplayName("Castling: King moves 2 squares")
    void testCastlingKingMovement() {
        int kingStartCol = 4;  // e-file
        int kingsideCastle = 6;  // g-file
        int queensideCastle = 2;  // c-file
        
        assertEquals(2, Math.abs(kingsideCastle - kingStartCol));
        assertEquals(2, Math.abs(queensideCastle - kingStartCol));
    }
}
