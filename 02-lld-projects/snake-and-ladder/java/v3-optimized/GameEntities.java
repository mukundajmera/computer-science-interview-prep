import java.util.*;

/**
 * SnakeV3 and LadderV3 Game - V1 Basic
 * 
 * Core game entities: DiceV3, PlayerV3, Board elements.
 */

/**
 * DiceV3 for generating random rolls.
 */
class DiceV3 {
    private final int minValue;
    private final int maxValue;
    private final Random random;

    public DiceV3() {
        this(1, 6);
    }

    public DiceV3(int minValue, int maxValue) {
        this.minValue = minValue;
        this.maxValue = maxValue;
        this.random = new Random();
    }

    public int roll() {
        return random.nextInt(maxValue - minValue + 1) + minValue;
    }

    public int getMinValue() {
        return minValue;
    }

    public int getMaxValue() {
        return maxValue;
    }
}

/**
 * Represents a player in the game.
 */
class PlayerV3 {
    private final String id;
    private final String name;
    private int position;

    public PlayerV3(String id, String name) {
        if (id == null || id.isEmpty()) {
            throw new IllegalArgumentException("PlayerV3 ID cannot be null or empty");
        }
        if (name == null || name.isEmpty()) {
            throw new IllegalArgumentException("PlayerV3 name cannot be null or empty");
        }
        this.id = id;
        this.name = name;
        this.position = 0; // Start off the board
    }

    public String getId() {
        return id;
    }

    public String getName() {
        return name;
    }

    public int getPosition() {
        return position;
    }

    public void moveTo(int newPosition) {
        this.position = newPosition;
    }

    @Override
    public String toString() {
        return name + " (Position: " + position + ")";
    }

    @Override
    public boolean equals(Object obj) {
        if (this == obj) return true;
        if (obj == null || getClass() != obj.getClass()) return false;
        PlayerV3 player = (PlayerV3) obj;
        return id.equals(player.id);
    }

    @Override
    public int hashCode() {
        return id.hashCode();
    }
}

/**
 * Represents a snake on the board.
 */
class SnakeV3 {
    private final int head;  // Higher position
    private final int tail;  // Lower position

    public SnakeV3(int head, int tail) {
        if (head <= tail) {
            throw new IllegalArgumentException("SnakeV3 head must be higher than tail");
        }
        if (head < 2 || tail < 1) {
            throw new IllegalArgumentException("Invalid snake positions");
        }
        this.head = head;
        this.tail = tail;
    }

    public int getHead() {
        return head;
    }

    public int getTail() {
        return tail;
    }

    @Override
    public String toString() {
        return "SnakeV3(" + head + " → " + tail + ")";
    }
}

/**
 * Represents a ladder on the board.
 */
class LadderV3 {
    private final int bottom;  // Lower position
    private final int top;     // Higher position

    public LadderV3(int bottom, int top) {
        if (bottom >= top) {
            throw new IllegalArgumentException("LadderV3 bottom must be lower than top");
        }
        if (bottom < 1) {
            throw new IllegalArgumentException("Invalid ladder positions");
        }
        this.bottom = bottom;
        this.top = top;
    }

    public int getBottom() {
        return bottom;
    }

    public int getTop() {
        return top;
    }

    @Override
    public String toString() {
        return "LadderV3(" + bottom + " → " + top + ")";
    }
}

/**
 * Game status enumeration.
 */
enum GameStatusV3 {
    NOT_STARTED,
    IN_PROGRESS,
    FINISHED
}
