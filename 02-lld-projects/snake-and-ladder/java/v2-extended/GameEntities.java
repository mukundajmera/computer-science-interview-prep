import java.util.*;

/**
 * SnakeV2 and LadderV2 Game - V1 Basic
 * 
 * Core game entities: DiceV2, PlayerV2, Board elements.
 */

/**
 * DiceV2 for generating random rolls.
 */
class DiceV2 {
    private final int minValue;
    private final int maxValue;
    private final Random random;

    public DiceV2() {
        this(1, 6);
    }

    public DiceV2(int minValue, int maxValue) {
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
class PlayerV2 {
    private final String id;
    private final String name;
    private int position;

    public PlayerV2(String id, String name) {
        if (id == null || id.isEmpty()) {
            throw new IllegalArgumentException("PlayerV2 ID cannot be null or empty");
        }
        if (name == null || name.isEmpty()) {
            throw new IllegalArgumentException("PlayerV2 name cannot be null or empty");
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
        PlayerV2 player = (PlayerV2) obj;
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
class SnakeV2 {
    private final int head;  // Higher position
    private final int tail;  // Lower position

    public SnakeV2(int head, int tail) {
        if (head <= tail) {
            throw new IllegalArgumentException("SnakeV2 head must be higher than tail");
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
        return "SnakeV2(" + head + " → " + tail + ")";
    }
}

/**
 * Represents a ladder on the board.
 */
class LadderV2 {
    private final int bottom;  // Lower position
    private final int top;     // Higher position

    public LadderV2(int bottom, int top) {
        if (bottom >= top) {
            throw new IllegalArgumentException("LadderV2 bottom must be lower than top");
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
        return "LadderV2(" + bottom + " → " + top + ")";
    }
}

/**
 * Game status enumeration.
 */
enum GameStatusV2 {
    NOT_STARTED,
    IN_PROGRESS,
    FINISHED
}

/**
 * Trampoline bounces player forward by a fixed amount.
 */
class Trampoline {
    private final int position;
    private final int bounce;

    public Trampoline(int position, int bounce) {
        if (position <= 0) {
            throw new IllegalArgumentException("Trampoline position must be positive");
        }
        this.position = position;
        this.bounce = bounce;
    }

    public int getPosition() {
        return position;
    }

    public int getBounce() {
        return bounce;
    }
}

/**
 * ElevatorLadder acts like a ladder but gives an extra turn or goes extremely high.
 * We'll implement it as just a class that Board knows about.
 */
class ElevatorLadder {
    private final int bottom;
    private final int top;

    public ElevatorLadder(int bottom, int top) {
        if (bottom >= top) {
            throw new IllegalArgumentException("ElevatorLadder bottom must be less than top");
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
}

/**
 * CrookedSnake acts like a snake but takes a winding path.
 */
class CrookedSnake {
    private final int head;
    private final int tail;

    public CrookedSnake(int head, int tail) {
        if (head <= tail) {
            throw new IllegalArgumentException("CrookedSnake head must be greater than tail");
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
}
