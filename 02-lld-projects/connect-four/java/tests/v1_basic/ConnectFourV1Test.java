import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

public class ConnectFourV1Test {

    @Test
    void rejectsInvalidColumnAndWrongTurn() {
        Player red = new Player("r", DiscColor.RED);
        Player yellow = new Player("y", DiscColor.YELLOW);
        Game game = new Game(red, yellow);

        assertFalse(game.makeMove(red, -1));
        assertFalse(game.makeMove(yellow, 0));
    }

    @Test
    void detectsVerticalWin() {
        Player red = new Player("r", DiscColor.RED);
        Player yellow = new Player("y", DiscColor.YELLOW);
        Game game = new Game(red, yellow);

        assertTrue(game.makeMove(red, 0));
        assertTrue(game.makeMove(yellow, 1));
        assertTrue(game.makeMove(red, 0));
        assertTrue(game.makeMove(yellow, 1));
        assertTrue(game.makeMove(red, 0));
        assertTrue(game.makeMove(yellow, 1));
        assertTrue(game.makeMove(red, 0));

        assertEquals(GameState.RED_WON, game.getGameState());
        assertEquals(red, game.getWinner());
        assertFalse(game.makeMove(yellow, 2));
    }
}
