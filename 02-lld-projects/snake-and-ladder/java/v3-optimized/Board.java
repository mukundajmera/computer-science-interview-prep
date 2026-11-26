import java.util.*;

/**
 * SnakeV3 and LadderV3 Game - V1 Basic
 * 
 * Board class managing snakes, ladders, and position calculations.
 */

/**
 * Game board with snakes and ladders.
 */
class BoardV3 {
    private final int size;
    private final Map<Integer, Integer> snakes;   // head -> tail
    private final Map<Integer, Integer> ladders;  // bottom -> top

    public BoardV3(int size) {
        if (size < 10) {
            throw new IllegalArgumentException("Board size must be at least 10");
        }
        this.size = size;
        this.snakes = new HashMap<>();
        this.ladders = new HashMap<>();
    }

    public BoardV3() {
        this(100);
    }

    public void addSnake(int head, int tail) {
        if (head <= tail) {
            throw new IllegalArgumentException("SnakeV3 head must be greater than tail");
        }
        if (head < 2 || tail < 1 || head > size) {
            throw new IllegalArgumentException("Invalid snake positions");
        }
        if (ladders.containsKey(head) || ladders.containsValue(head)) {
            throw new IllegalArgumentException("Cannot place snake on ladder position");
        }
        snakes.put(head, tail);
    }

    public void addLadder(int bottom, int top) {
        if (bottom >= top) {
            throw new IllegalArgumentException("LadderV3 bottom must be less than top");
        }
        if (bottom < 1 || top > size) {
            throw new IllegalArgumentException("Invalid ladder positions");
        }
        if (snakes.containsKey(bottom) || snakes.containsValue(bottom)) {
            throw new IllegalArgumentException("Cannot place ladder on snake position");
        }
        ladders.put(bottom, top);
    }

    public void addSnake(SnakeV3 snake) {
        addSnake(snake.getHead(), snake.getTail());
    }

    public void addLadder(LadderV3 ladder) {
        addLadder(ladder.getBottom(), ladder.getTop());
    }

    /**
     * Calculate the next position after a dice roll.
     * Applies snake/ladder effects.
     */
    public int getNextPosition(int currentPosition, int diceRoll, boolean quiet) {
        int newPosition = currentPosition + diceRoll;
        
        // Check if exceeds board size (stay in place)
        if (newPosition > size) {
            return currentPosition;
        }
        
        // Check for snake
        if (snakes.containsKey(newPosition)) {
            int snakeTail = snakes.get(newPosition);
            if(!quiet) System.out.println("  Oops! SnakeV3 at " + newPosition + " → slides down to " + snakeTail);
            return snakeTail;
        }
        
        // Check for ladder
        if (ladders.containsKey(newPosition)) {
            int ladderTop = ladders.get(newPosition);
            if(!quiet) System.out.println("  Yay! LadderV3 at " + newPosition + " → climbs up to " + ladderTop);
            return ladderTop;
        }
        
        return newPosition;
    }

    public boolean hasSnakeAt(int position) {
        return snakes.containsKey(position);
    }

    public boolean hasLadderAt(int position) {
        return ladders.containsKey(position);
    }

    public boolean isWinningPosition(int position) {
        return position == size;
    }

    public int getSize() {
        return size;
    }

    public int getSnakeCount() {
        return snakes.size();
    }

    public int getLadderCount() {
        return ladders.size();
    }

    public void displayBoard() {
        System.out.println("\n=== Board Configuration ===");
        System.out.println("Size: " + size + " squares");
        System.out.println("Snakes (" + snakes.size() + "):");
        for (Map.Entry<Integer, Integer> entry : snakes.entrySet()) {
            System.out.println("  " + entry.getKey() + " → " + entry.getValue());
        }
        System.out.println("Ladders (" + ladders.size() + "):");
        for (Map.Entry<Integer, Integer> entry : ladders.entrySet()) {
            System.out.println("  " + entry.getKey() + " → " + entry.getValue());
        }
    }

    /**
     * Create a standard board with predefined snakes and ladders.
     */
    public static BoardV3 createStandardBoard() {
        BoardV3 board = new BoardV3(100);
        
        // Add snakes (head -> tail)
        board.addSnake(16, 6);
        board.addSnake(47, 26);
        board.addSnake(49, 11);
        board.addSnake(56, 53);
        board.addSnake(62, 19);
        board.addSnake(64, 60);
        board.addSnake(87, 24);
        board.addSnake(93, 73);
        board.addSnake(95, 75);
        board.addSnake(98, 78);
        
        // Add ladders (bottom -> top)
        board.addLadder(1, 38);
        board.addLadder(4, 14);
        board.addLadder(9, 31);
        board.addLadder(21, 42);
        board.addLadder(28, 84);
        board.addLadder(36, 44);
        board.addLadder(51, 67);
        board.addLadder(71, 91);
        board.addLadder(80, 100);
        
        return board;
    }
}
