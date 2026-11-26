/**
 * Abstract base class for players.
 */
public abstract class Player {
    private final String name;
    private final Mark mark;

    public Player(String name, Mark mark) {
        if (mark == Mark.EMPTY) {
            throw new IllegalArgumentException("Player cannot have EMPTY mark");
        }
        this.name = name;
        this.mark = mark;
    }

    public String getName() {
        return name;
    }

    public Mark getMark() {
        return mark;
    }

    /**
     * Get the next move from this player.
     * 
     * @param board Current board state
     * @return Position to place mark
     */
    public abstract Position makeMove(Board board);

    @Override
    public String toString() {
        return name + " (" + mark + ")";
    }
}
