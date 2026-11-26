import java.util.*;

/**
 * Snake and Ladder Game - V2 Extended
 * 
 * Board class managing snakes, ladders, trampolines, elevators, and position calculations.
 */
class BoardV2 {
    private final int size;
    private final Map<Integer, Integer> snakes;
    private final Map<Integer, Integer> ladders;
    private final Map<Integer, Integer> trampolines;
    private final Map<Integer, Integer> elevatorLadders;
    private final Map<Integer, Integer> crookedSnakes;

    public BoardV2(int size) {
        if (size < 10) {
            throw new IllegalArgumentException("Board size must be at least 10");
        }
        this.size = size;
        this.snakes = new HashMap<>();
        this.ladders = new HashMap<>();
        this.trampolines = new HashMap<>();
        this.elevatorLadders = new HashMap<>();
        this.crookedSnakes = new HashMap<>();
    }

    public void addSnake(SnakeV2 snake) {
        snakes.put(snake.getHead(), snake.getTail());
    }

    public void addLadder(LadderV2 ladder) {
        ladders.put(ladder.getBottom(), ladder.getTop());
    }

    public void addTrampoline(Trampoline trampoline) {
        trampolines.put(trampoline.getPosition(), trampoline.getBounce());
    }

    public void addElevatorLadder(ElevatorLadder elevator) {
        elevatorLadders.put(elevator.getBottom(), elevator.getTop());
    }

    public void addCrookedSnake(CrookedSnake snake) {
        crookedSnakes.put(snake.getHead(), snake.getTail());
    }

    public int getNextPosition(int currentPosition, int diceRoll) {
        int nextPosition = currentPosition + diceRoll;

        if (nextPosition > size) {
            return currentPosition;
        }

        while (true) {
            if (snakes.containsKey(nextPosition)) {
                System.out.println("  Oops! Snake at " + nextPosition + " -> slides down to " + snakes.get(nextPosition));
                nextPosition = snakes.get(nextPosition);
            } else if (ladders.containsKey(nextPosition)) {
                System.out.println("  Yay! Ladder at " + nextPosition + " -> climbs up to " + ladders.get(nextPosition));
                nextPosition = ladders.get(nextPosition);
            } else if (trampolines.containsKey(nextPosition)) {
                int bounce = trampolines.get(nextPosition);
                int bouncedPos = Math.min(size, nextPosition + bounce);
                System.out.println("  Boing! Trampoline at " + nextPosition + " -> bounces forward by " + bounce + " to " + bouncedPos);
                nextPosition = bouncedPos;
            } else if (elevatorLadders.containsKey(nextPosition)) {
                System.out.println("  Whoosh! Elevator Ladder at " + nextPosition + " -> shoots up to " + elevatorLadders.get(nextPosition));
                nextPosition = elevatorLadders.get(nextPosition);
            } else if (crookedSnakes.containsKey(nextPosition)) {
                System.out.println("  Yikes! Crooked Snake at " + nextPosition + " -> twists down to " + crookedSnakes.get(nextPosition));
                nextPosition = crookedSnakes.get(nextPosition);
            } else {
                break;
            }
        }
        return nextPosition;
    }

    public boolean isWinningPosition(int position) {
        return position == size;
    }

    public int getSize() {
        return size;
    }

    public void displayBoard() {
        System.out.println("\n=== BoardV2 Configuration ===");
        System.out.println("Size: " + size);
        System.out.println("Snakes: " + snakes.size());
        System.out.println("Ladders: " + ladders.size());
        System.out.println("Trampolines: " + trampolines.size());
        System.out.println("Elevator Ladders: " + elevatorLadders.size());
        System.out.println("Crooked Snakes: " + crookedSnakes.size());
        System.out.println("===========================\n");
    }

    public static BoardV2 createStandardBoard() {
        BoardV2 board = new BoardV2(100);
        board.addSnake(new SnakeV2(16, 6));
        board.addSnake(new SnakeV2(47, 26));
        board.addSnake(new SnakeV2(49, 11));
        board.addSnake(new SnakeV2(56, 53));
        board.addSnake(new SnakeV2(62, 19));
        board.addSnake(new SnakeV2(64, 60));
        board.addSnake(new SnakeV2(87, 24));
        board.addSnake(new SnakeV2(93, 73));
        board.addSnake(new SnakeV2(95, 75));
        board.addSnake(new SnakeV2(98, 78));
        
        board.addLadder(new LadderV2(1, 38));
        board.addLadder(new LadderV2(4, 14));
        board.addLadder(new LadderV2(9, 31));
        board.addLadder(new LadderV2(21, 42));
        board.addLadder(new LadderV2(28, 84));
        board.addLadder(new LadderV2(36, 44));
        board.addLadder(new LadderV2(51, 67));
        board.addLadder(new LadderV2(71, 91));
        board.addLadder(new LadderV2(80, 100));

        // V2 Extended elements
        board.addTrampoline(new Trampoline(15, 5));
        board.addTrampoline(new Trampoline(30, 8));
        board.addElevatorLadder(new ElevatorLadder(20, 70));
        board.addCrookedSnake(new CrookedSnake(99, 10));

        return board;
    }
}
