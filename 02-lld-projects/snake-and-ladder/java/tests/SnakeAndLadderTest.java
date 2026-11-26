import java.util.*;

/**
 * Custom assertions for testing without JUnit.
 */
class Assertions {
    public static void assertTrue(boolean condition) {
        if (!condition) throw new AssertionError("Expected true, got false");
    }
    public static void assertFalse(boolean condition) {
        if (condition) throw new AssertionError("Expected false, got true");
    }
    public static void assertEquals(Object expected, Object actual) {
        if (!Objects.equals(expected, actual)) {
            throw new AssertionError("Expected " + expected + ", got " + actual);
        }
    }
    public static void assertNotNull(Object obj) {
        if (obj == null) throw new AssertionError("Expected non-null, got null");
    }
    public static void assertThrows(Class<? extends Exception> expectedType, Runnable executable) {
        try {
            executable.run();
        } catch (Exception e) {
            if (expectedType.isInstance(e)) {
                return;
            }
            throw new AssertionError("Expected " + expectedType.getName() + " but got " + e.getClass().getName());
        }
        throw new AssertionError("Expected " + expectedType.getName() + " to be thrown, but nothing was thrown.");
    }
}

/**
 * Unit tests for Snake and Ladder Game
 */
public class SnakeAndLadderTest {

    public static void main(String[] args) {
        System.out.println("Running SnakeAndLadderTest...");
        SnakeAndLadderTest test = new SnakeAndLadderTest();
        test.testDiceRollRange();
        test.testPlayerCreation();
        test.testPlayerMovement();
        test.testSnakeCreation();
        test.testSnakeInvalidPositions();
        test.testLadderCreation();
        test.testLadderInvalidPositions();
        test.testBoardNextPosition();
        test.testBoardSnakeEffect();
        test.testBoardLadderEffect();
        test.testBoardBeyondSize();
        test.testBoardWinningPosition();
        test.testStandardBoardCreation();
        test.testGameMinimumPlayers();
        test.testGameAddPlayers();
        test.testGameStart();
        test.testGamePlayTurn();
        test.testGameDetectsWinner();
        test.testFullGameWorkflow();
        System.out.println("All tests passed!");
    }

    void testDiceRollRange() {
        Dice dice = new Dice();
        for (int i = 0; i < 100; i++) {
            int roll = dice.roll();
            Assertions.assertTrue(roll >= 1 && roll <= 6);
        }
    }

    void testPlayerCreation() {
        Player player = new Player("P1", "Alice");
        Assertions.assertEquals("P1", player.getId());
        Assertions.assertEquals("Alice", player.getName());
        Assertions.assertEquals(0, player.getPosition());
    }

    void testPlayerMovement() {
        Player player = new Player("P1", "Alice");
        player.moveTo(10);
        Assertions.assertEquals(10, player.getPosition());
        player.moveTo(50);
        Assertions.assertEquals(50, player.getPosition());
    }

    void testSnakeCreation() {
        Snake snake = new Snake(16, 6);
        Assertions.assertEquals(16, snake.getHead());
        Assertions.assertEquals(6, snake.getTail());
    }

    void testSnakeInvalidPositions() {
        Assertions.assertThrows(IllegalArgumentException.class, () -> new Snake(6, 16));
        Assertions.assertThrows(IllegalArgumentException.class, () -> new Snake(10, 10));
    }

    void testLadderCreation() {
        Ladder ladder = new Ladder(4, 14);
        Assertions.assertEquals(4, ladder.getBottom());
        Assertions.assertEquals(14, ladder.getTop());
    }

    void testLadderInvalidPositions() {
        Assertions.assertThrows(IllegalArgumentException.class, () -> new Ladder(14, 4));
        Assertions.assertThrows(IllegalArgumentException.class, () -> new Ladder(10, 10));
    }

    void testBoardNextPosition() {
        Board board = new Board(100);
        Assertions.assertEquals(5, board.getNextPosition(0, 5));
        Assertions.assertEquals(15, board.getNextPosition(10, 5));
    }

    void testBoardSnakeEffect() {
        Board board = new Board(100);
        board.addSnake(new Snake(16, 6));
        Assertions.assertEquals(6, board.getNextPosition(10, 6));
    }

    void testBoardLadderEffect() {
        Board board = new Board(100);
        board.addLadder(new Ladder(4, 14));
        Assertions.assertEquals(14, board.getNextPosition(0, 4));
    }

    void testBoardBeyondSize() {
        Board board = new Board(100);
        Assertions.assertEquals(98, board.getNextPosition(98, 5));
    }

    void testBoardWinningPosition() {
        Board board = new Board(100);
        Assertions.assertTrue(board.isWinningPosition(100));
        Assertions.assertFalse(board.isWinningPosition(99));
    }

    void testStandardBoardCreation() {
        Board board = Board.createStandardBoard();
        Assertions.assertEquals(100, board.getSize());
        Assertions.assertTrue(board.hasSnakeAt(16));
        Assertions.assertTrue(board.hasLadderAt(1));
    }

    void testGameMinimumPlayers() {
        Game game = new Game();
        game.addPlayer("Alice");
        Assertions.assertThrows(IllegalStateException.class, () -> game.startGame());
    }

    void testGameAddPlayers() {
        Game game = new Game();
        Player p1 = game.addPlayer("Alice");
        Player p2 = game.addPlayer("Bob");
        Assertions.assertEquals(2, game.getPlayers().size());
        Assertions.assertEquals("Alice", p1.getName());
        Assertions.assertEquals("Bob", p2.getName());
    }

    void testGameStart() {
        Game game = new Game();
        game.addPlayer("Alice");
        game.addPlayer("Bob");
        game.startGame();
        Assertions.assertEquals(GameStatus.IN_PROGRESS, game.getStatus());
    }

    void testGamePlayTurn() {
        Game game = new Game();
        game.addPlayer("Alice");
        game.addPlayer("Bob");
        game.startGame();
        Player firstPlayer = game.getCurrentPlayer();
        game.playTurn();
        Assertions.assertTrue(firstPlayer.getPosition() >= 0);
    }

    void testGameDetectsWinner() {
        Board board = new Board(10);
        board.addLadder(new Ladder(1, 10));
        Game game = new Game(board);
        game.addPlayer("Alice");
        game.addPlayer("Bob");
        game.startGame();
        int maxTurns = 100;
        int turns = 0;
        while (!game.isGameOver() && turns < maxTurns) {
            game.playTurn();
            turns++;
        }
        if (game.isGameOver()) {
            Assertions.assertNotNull(game.getWinner());
        }
    }

    void testFullGameWorkflow() {
        Game game = new Game();
        game.addPlayer("Alice");
        game.addPlayer("Bob");
        game.addPlayer("Charlie");
        Assertions.assertEquals(GameStatus.NOT_STARTED, game.getStatus());
        Assertions.assertEquals(3, game.getPlayers().size());
        game.startGame();
        Assertions.assertEquals(GameStatus.IN_PROGRESS, game.getStatus());
        for (int i = 0; i < 10 && !game.isGameOver(); i++) {
            game.playTurn();
        }
        for (Player player : game.getPlayers()) {
            Assertions.assertTrue(player.getPosition() >= 0);
        }
    }
}
