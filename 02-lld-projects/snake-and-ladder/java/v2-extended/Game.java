import java.util.*;

/**
 * SnakeV2 and LadderV2 Game - V1 Basic
 * 
 * Main Game class managing gameplay.
 */

/**
 * Main game controller.
 */
class GameV2 {
    private final BoardV2 board;
    private final List<PlayerV2> players;
    private final DiceV2 dice;
    private int currentPlayerIndex;
    private GameStatusV2 status;
    private PlayerV2 winner;

    public GameV2(BoardV2 board) {
        this.board = board;
        this.players = new ArrayList<>();
        this.dice = new DiceV2();
        this.currentPlayerIndex = 0;
        this.status = GameStatusV2.NOT_STARTED;
        this.winner = null;
    }

    public GameV2() {
        this(BoardV2.createStandardBoard());
    }

    /**
     * Add a player to the game.
     */
    public PlayerV2 addPlayer(String name) {
        if (status != GameStatusV2.NOT_STARTED) {
            throw new IllegalStateException("Cannot add players after game has started");
        }
        if (name == null || name.isEmpty()) {
            throw new IllegalArgumentException("PlayerV2 name cannot be null or empty");
        }
        
        String id = "P" + (players.size() + 1);
        PlayerV2 player = new PlayerV2(id, name);
        players.add(player);
        System.out.println("Added player: " + name);
        return player;
    }

    /**
     * Start the game.
     */
    public void startGame() {
        if (players.size() < 2) {
            throw new IllegalStateException("Need at least 2 players to start");
        }
        status = GameStatusV2.IN_PROGRESS;
        currentPlayerIndex = 0;
        System.out.println("\n=== Game Started! ===");
        System.out.println("Players: " + players.size());
        System.out.println("First turn: " + getCurrentPlayer().getName());
    }

    /**
     * Play the current player's turn.
     */
    public void playTurn() {
        if (status != GameStatusV2.IN_PROGRESS) {
            throw new IllegalStateException("Game is not in progress");
        }

        PlayerV2 currentPlayer = getCurrentPlayer();
        int roll = dice.roll();
        int oldPosition = currentPlayer.getPosition();
        int newPosition = board.getNextPosition(oldPosition, roll);

        System.out.println("\n" + currentPlayer.getName() + " rolls " + roll);
        System.out.println("  Position: " + oldPosition + " → " + newPosition);
        
        currentPlayer.moveTo(newPosition);

        // Check for win
        if (board.isWinningPosition(newPosition)) {
            status = GameStatusV2.FINISHED;
            winner = currentPlayer;
            System.out.println("\n🎉 " + currentPlayer.getName() + " WINS! 🎉");
            return;
        }

        // Move to next player
        currentPlayerIndex = (currentPlayerIndex + 1) % players.size();
    }

    /**
     * Roll the dice.
     */
    public int rollDice() {
        return dice.roll();
    }

    /**
     * Get the current player.
     */
    public PlayerV2 getCurrentPlayer() {
        return players.get(currentPlayerIndex);
    }

    /**
     * Check if game is over.
     */
    public boolean isGameOver() {
        return status == GameStatusV2.FINISHED;
    }

    /**
     * Get the winner.
     */
    public PlayerV2 getWinner() {
        return winner;
    }

    /**
     * Get game status.
     */
    public GameStatusV2 getStatus() {
        return status;
    }

    /**
     * Get all players.
     */
    public List<PlayerV2> getPlayers() {
        return Collections.unmodifiableList(players);
    }

    /**
     * Get the board.
     */
    public BoardV2 getBoard() {
        return board;
    }

    /**
     * Display current game status.
     */
    public void displayStatus() {
        System.out.println("\n=== Game Status ===");
        System.out.println("Status: " + status);
        System.out.println("Players:");
        for (PlayerV2 player : players) {
            String marker = (player == getCurrentPlayer()) ? " ← Current" : "";
            System.out.println("  " + player + marker);
        }
        if (winner != null) {
            System.out.println("Winner: " + winner.getName());
        }
    }

    /**
     * Play the game until someone wins.
     */
    public PlayerV2 playGame() {
        startGame();
        
        int maxTurns = 1000; // Prevent infinite loops
        int turnCount = 0;
        
        while (!isGameOver() && turnCount < maxTurns) {
            playTurn();
            turnCount++;
        }
        
        if (turnCount >= maxTurns) {
            System.out.println("Game ended - max turns reached");
        }
        
        return getWinner();
    }
}
