/**
 * Lightweight coordinator for interview discussions on game-flow extension.
 */
public class GameFlowCoordinator {
    private final TurnPolicy turnPolicy;
    private final WinResolutionPolicy winResolutionPolicy;

    public GameFlowCoordinator(TurnPolicy turnPolicy, WinResolutionPolicy winResolutionPolicy) {
        this.turnPolicy = turnPolicy;
        this.winResolutionPolicy = winResolutionPolicy;
    }

    public GameStateTransition onMove(Object gameState, Object position) {
        Object nextTurn = turnPolicy.nextTurn(gameState);
        boolean win = winResolutionPolicy.isWinningMove(gameState, position);
        return new GameStateTransition(nextTurn, win);
    }
}

interface TurnPolicy {
    Object nextTurn(Object gameState);
}

interface WinResolutionPolicy {
    boolean isWinningMove(Object gameState, Object position);
}

final class GameStateTransition {
    private final Object nextTurn;
    private final boolean win;

    GameStateTransition(Object nextTurn, boolean win) {
        this.nextTurn = nextTurn;
        this.win = win;
    }

    public Object nextTurn() {
        return nextTurn;
    }

    public boolean hasWinner() {
        return win;
    }
}
