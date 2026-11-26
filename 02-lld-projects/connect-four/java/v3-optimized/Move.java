public class Move {
    private final Player player;
    private final int row;
    private final int column;

    public Move(Player player, int row, int column) {
        this.player = player;
        this.row = row;
        this.column = column;
    }

    public Player getPlayer() {
        return player;
    }

    public int getRow() {
        return row;
    }

    public int getColumn() {
        return column;
    }
}
