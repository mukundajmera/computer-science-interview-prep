public enum DiscColor {
    RED,
    YELLOW,
    EMPTY;

    public DiscColor opposite() {
        if (this == RED) return YELLOW;
        if (this == YELLOW) return RED;
        return EMPTY;
    }
}
