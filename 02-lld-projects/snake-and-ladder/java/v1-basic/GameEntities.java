import java.util.*;

/**
 * Snake and Ladder Game - V1 Basic
 * 
 * Core game entities: Dice, Player, Board elements.
 */

/**
 * Dice for generating random rolls.
 */
class Dice {
    private final int minValue;
    private final int maxValue;
    private final Random random;

    public Dice() {
        this(1, 6);
    }

    public Dice(int minValue, int maxValue) {
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
class Player {
    private final String id;
    private final String name;
    private int position;

    public Player(String id, String name) {
        if (id == null || id.isEmpty()) {
            throw new IllegalArgumentException("Player ID cannot be null or empty");
        }
        if (name == null || name.isEmpty()) {
            throw new IllegalArgumentException("Player name cannot be null or empty");
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
        Player player = (Player) obj;
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
class Snake {
    private final int head;  // Higher position
    private final int tail;  // Lower position

    public Snake(int head, int tail) {
        if (head <= tail) {
            throw new IllegalArgumentException("Snake head must be higher than tail");
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
        return "Snake(" + head + " → " + tail + ")";
    }
}

/**
 * Represents a ladder on the board.
 */
class Ladder {
    private final int bottom;  // Lower position
    private final int top;     // Higher position

    public Ladder(int bottom, int top) {
        if (bottom >= top) {
            throw new IllegalArgumentException("Ladder bottom must be lower than top");
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
        return "Ladder(" + bottom + " → " + top + ")";
    }
}

/**
 * Game status enumeration.
 */
enum GameStatus {
    NOT_STARTED,
    IN_PROGRESS,
    FINISHED
}
