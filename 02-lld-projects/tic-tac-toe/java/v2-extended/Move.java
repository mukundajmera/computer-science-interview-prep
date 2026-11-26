/**
 * Represents a move in the game (Command pattern).
 */
public class Move {
    private final Position position;
    private final Player player;
    private final Mark mark;
    private final long timestamp;

    public Move(Position position, Player player, Mark mark) {
        this.position = position;
        this.player = player;
        this.mark = mark;
        this.timestamp = System.currentTimeMillis();
    }

    public Position getPosition() {
        return position;
    }

    public Player getPlayer() {
        return player;
    }

    public Mark getMark() {
        return mark;
    }

    public long getTimestamp() {
        return timestamp;
    }

    @Override
    public String toString() {
        return player.getName() + " placed " + mark + " at " + position;
    }
}
