import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;

/**
 * Manages multiple concurrent game sessions.
 */
public class GameSession {
    private static GameSession instance;
    private final Map<String, Game> activeGames;
    private int gameCounter;

    private GameSession() {
        this.activeGames = new ConcurrentHashMap<>();
        this.gameCounter = 0;
    }

    public static synchronized GameSession getInstance() {
        if (instance == null) {
            instance = new GameSession();
        }
        return instance;
    }

    /**
     * Create a new game.
     */
    public synchronized Game createGame(Player player1, Player player2, int boardSize) {
        String gameId = "GAME-" + (++gameCounter);
        Game game = new Game(gameId, player1, player2, boardSize);
        activeGames.put(gameId, game);
        return game;
    }

    /**
     * Get a game by ID.
     */
    public Game getGame(String gameId) {
        return activeGames.get(gameId);
    }

    /**
     * Remove a finished game.
     */
    public void removeGame(String gameId) {
        activeGames.remove(gameId);
    }

    /**
     * Get count of active games.
     */
    public int getActiveGameCount() {
        return activeGames.size();
    }

    /**
     * Get all active game IDs.
     */
    public String[] getActiveGameIds() {
        return activeGames.keySet().toArray(new String[0]);
    }
}
