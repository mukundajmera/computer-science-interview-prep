/**
 * Represents the game state.
 */
public enum GameState {
    NOT_STARTED,
    IN_PROGRESS,
    X_WON,
    O_WON,
    DRAW;

    public boolean isGameOver() {
        return this == X_WON || this == O_WON || this == DRAW;
    }

    public String getMessage() {
        switch (this) {
            case X_WON:
                return "Player X wins!";
            case O_WON:
                return "Player O wins!";
            case DRAW:
                return "It's a draw!";
            case IN_PROGRESS:
                return "Game in progress...";
            default:
                return "Game not started";
        }
    }
}
