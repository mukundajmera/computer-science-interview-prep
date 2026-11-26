public enum GameState {
    IN_PROGRESS,
    RED_WON,
    YELLOW_WON,
    DRAW;

    public boolean isTerminal() {
        return this == RED_WON || this == YELLOW_WON || this == DRAW;
    }
}
