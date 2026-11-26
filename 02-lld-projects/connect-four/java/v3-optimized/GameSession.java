public class GameSession {
    private final String sessionId;
    private final Game game;

    public GameSession(String sessionId, Game game) {
        this.sessionId = sessionId;
        this.game = game;
    }

    public String getSessionId() {
        return sessionId;
    }

    public Game getGame() {
        return game;
    }
}
