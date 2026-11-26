import java.util.*;

/**
 * SnakeV3 and LadderV3 Game - V1 Basic
 * 
 * Main Game class managing gameplay.
 */

/**
 * Main game controller.
 */
class GameV3 {
    private final BoardV3 board;
    private final List<PlayerV3> players;
    private final DiceV3 dice;
    private int currentPlayerIndex;
    private GameStatusV3 status;
    private PlayerV3 winner;
    private boolean quietMode = false;
    public void setQuietMode(boolean quietMode) { this.quietMode = quietMode; }

    public GameV3(BoardV3 board) {
        this.board = board;
        this.players = new ArrayList<>();
        this.dice = new DiceV3();
        this.currentPlayerIndex = 0;
        this.status = GameStatusV3.NOT_STARTED;
        this.winner = null;
    }

    public GameV3() {
        this(BoardV3.createStandardBoard());
    }

    /**
     * Add a player to the game.
     */
    public PlayerV3 addPlayer(String name) {
        if (status != GameStatusV3.NOT_STARTED) {
            throw new IllegalStateException("Cannot add players after game has started");
        }
        if (name == null || name.isEmpty()) {
            throw new IllegalArgumentException("PlayerV3 name cannot be null or empty");
        }
        
        String id = "P" + (players.size() + 1);
        PlayerV3 player = new PlayerV3(id, name);
        players.add(player);
        if(!quietMode) System.out.println("Added player: " + name);
        return player;
    }

    /**
     * Start the game.
     */
    public void startGame() {
        if (players.size() < 2) {
            throw new IllegalStateException("Need at least 2 players to start");
        }
        status = GameStatusV3.IN_PROGRESS;
        currentPlayerIndex = 0;
        if(!quietMode) System.out.println("\n=== Game Started! ===");
        if(!quietMode) System.out.println("Players: " + players.size());
        if(!quietMode) System.out.println("First turn: " + getCurrentPlayer().getName());
    }

    /**
     * Play the current player's turn.
     */
    public void playTurn() {
        playTurn(false);
    }

    public void playTurn(boolean quietArg)  {
        if (status != GameStatusV3.IN_PROGRESS) {
            throw new IllegalStateException("Game is not in progress");
        }

        PlayerV3 currentPlayer = getCurrentPlayer();
        int roll = dice.roll();
        int oldPosition = currentPlayer.getPosition();
        int newPosition = board.getNextPosition(oldPosition, roll, quietMode || quietArg);

        if(!quietMode && !quietArg) System.out.println("\n" + currentPlayer.getName() + " rolls " + roll);
        if(!quietMode && !quietArg) System.out.println("  Position: " + oldPosition + " → " + newPosition);
        
        currentPlayer.moveTo(newPosition);

        // Check for win
        if (board.isWinningPosition(newPosition)) {
            status = GameStatusV3.FINISHED;
            winner = currentPlayer;
            if(!quietMode && !quietArg) System.out.println("\n🎉 " + currentPlayer.getName() + " WINS! 🎉");
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
    public PlayerV3 getCurrentPlayer() {
        return players.get(currentPlayerIndex);
    }

    /**
     * Check if game is over.
     */
    public boolean isGameOver() {
        return status == GameStatusV3.FINISHED;
    }

    /**
     * Get the winner.
     */
    public PlayerV3 getWinner() {
        return winner;
    }

    /**
     * Get game status.
     */
    public GameStatusV3 getStatus() {
        return status;
    }

    /**
     * Get all players.
     */
    public List<PlayerV3> getPlayers() {
        return Collections.unmodifiableList(players);
    }

    /**
     * Get the board.
     */
    public BoardV3 getBoard() {
        return board;
    }

    /**
     * Display current game status.
     */
    public void displayStatus() {
        System.out.println("\n=== Game Status ===");
        System.out.println("Status: " + status);
        System.out.println("Players:");
        for (PlayerV3 player : players) {
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
    public PlayerV3 playGame() {
        startGame();
        
        int maxTurns = 1000; // Prevent infinite loops
        int turnCount = 0;
        
        while (!isGameOver() && turnCount < maxTurns) {
            playTurn(false);
            turnCount++;
        }
        
        if (turnCount >= maxTurns) {
            System.out.println("Game ended - max turns reached");
        }
        
        return getWinner();
    }
}
