import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

public class ConnectFourV3Test {

    @Test
    void suggestedBotMoveIsLegal() {
        Player red = new Player("r", DiscColor.RED);
        Player yellow = new Player("y", DiscColor.YELLOW);
        Game game = new Game(red, yellow);

        int col = game.suggestBotMove();
        assertTrue(col >= 0);
        assertTrue(game.getBoard().canPlace(col));
    }

    @Test
    void sessionKeepsGameReference() {
        Player red = new Player("r", DiscColor.RED);
        Player yellow = new Player("y", DiscColor.YELLOW);
        Game game = new Game(red, yellow);
        GameSession session = new GameSession("s-1", game);

        assertEquals("s-1", session.getSessionId());
        assertSame(game, session.getGame());
    }
}
