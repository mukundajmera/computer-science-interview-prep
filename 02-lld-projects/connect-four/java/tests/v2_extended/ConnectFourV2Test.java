import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

public class ConnectFourV2Test {

    @Test
    void undoRestoresTurnAndState() {
        Player red = new Player("r", DiscColor.RED);
        Player yellow = new Player("y", DiscColor.YELLOW);
        Game game = new Game(red, yellow, new Board(6, 7));

        assertTrue(game.makeMove(red, 2));
        assertTrue(game.makeMove(yellow, 3));
        assertEquals(red, game.getMoveHistory().get(0).getPlayer());
        assertEquals(yellow, game.getMoveHistory().get(1).getPlayer());

        assertTrue(game.undoLastMove());
        assertEquals(yellow, game.getCurrentPlayer());
        assertEquals(GameState.IN_PROGRESS, game.getGameState());
    }
}
