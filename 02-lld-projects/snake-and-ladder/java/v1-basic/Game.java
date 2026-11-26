import java.util.*;

/**
 * Snake and Ladder Game - V1 Basic
 * 
 * Main Game class managing gameplay.
 */

/**
 * Main game controller.
 */
class Game {
    private final Board board;
    private final List<Player> players;
    private final Dice dice;
    private int currentPlayerIndex;
    private GameStatus status;
    private Player winner;

    public Game(Board board) {
        this.board = board;
        this.players = new ArrayList<>();
        this.dice = new Dice();
        this.currentPlayerIndex = 0;
        this.status = GameStatus.NOT_STARTED;
        this.winner = null;
    }

    public Game() {
        this(Board.createStandardBoard());
    }

    /**
     * Add a player to the game.
     */
    public Player addPlayer(String name) {
        if (status != GameStatus.NOT_STARTED) {
            throw new IllegalStateException("Cannot add players after game has started");
        }
        if (name == null || name.isEmpty()) {
            throw new IllegalArgumentException("Player name cannot be null or empty");
        }
        
        String id = "P" + (players.size() + 1);
        Player player = new Player(id, name);
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
        status = GameStatus.IN_PROGRESS;
        currentPlayerIndex = 0;
        System.out.println("\n=== Game Started! ===");
        System.out.println("Players: " + players.size());
        System.out.println("First turn: " + getCurrentPlayer().getName());
    }

    /**
     * Play the current player's turn.
     */
    public void playTurn() {
        if (status != GameStatus.IN_PROGRESS) {
            throw new IllegalStateException("Game is not in progress");
        }

        Player currentPlayer = getCurrentPlayer();
        int roll = dice.roll();
        int oldPosition = currentPlayer.getPosition();
        int newPosition = board.getNextPosition(oldPosition, roll);

        System.out.println("\n" + currentPlayer.getName() + " rolls " + roll);
        System.out.println("  Position: " + oldPosition + " → " + newPosition);
        
        currentPlayer.moveTo(newPosition);

        // Check for win
        if (board.isWinningPosition(newPosition)) {
            status = GameStatus.FINISHED;
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
    public Player getCurrentPlayer() {
        return players.get(currentPlayerIndex);
    }

    /**
     * Check if game is over.
     */
    public boolean isGameOver() {
        return status == GameStatus.FINISHED;
    }

    /**
     * Get the winner.
     */
    public Player getWinner() {
        return winner;
    }

    /**
     * Get game status.
     */
    public GameStatus getStatus() {
        return status;
    }

    /**
     * Get all players.
     */
    public List<Player> getPlayers() {
        return Collections.unmodifiableList(players);
    }

    /**
     * Get the board.
     */
    public Board getBoard() {
        return board;
    }

    /**
     * Display current game status.
     */
    public void displayStatus() {
        System.out.println("\n=== Game Status ===");
        System.out.println("Status: " + status);
        System.out.println("Players:");
        for (Player player : players) {
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
    public Player playGame() {
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
