/**
 * Main game controller for Tic-Tac-Toe.
 */
public class Game {
    private final Board board;
    private final Player[] players;
    private int currentPlayerIndex;
    private GameState state;
    private final WinChecker winChecker;
    private Position lastMove;

    public Game(Player player1, Player player2) {
        this(player1, player2, Board.DEFAULT_SIZE);
    }

    public Game(Player player1, Player player2, int boardSize) {
        this.board = new Board(boardSize);
        this.players = new Player[]{player1, player2};
        this.winChecker = new WinChecker();
        this.state = GameState.NOT_STARTED;
        this.currentPlayerIndex = 0;
        this.lastMove = null;
    }

    /**
     * Start the game.
     */
    public void start() {
        state = GameState.IN_PROGRESS;
        System.out.println("Game Started! " + players[0].getMark() + " moves first.");
    }

    /**
     * Make a move at the specified position.
     * 
     * @param position Position to place the mark
     * @return true if move was successful
     */
    public boolean makeMove(Position position) {
        if (state != GameState.IN_PROGRESS) {
            System.out.println("Game is not in progress!");
            return false;
        }

        Player currentPlayer = getCurrentPlayer();
        
        if (!board.placeMark(position, currentPlayer.getMark())) {
            System.out.println("Invalid move!");
            return false;
        }

        lastMove = position;

        // Check for win
        if (winChecker.checkWin(board, position)) {
            state = (currentPlayer.getMark() == Mark.X) ? GameState.X_WON : GameState.O_WON;
        } else if (board.isFull()) {
            state = GameState.DRAW;
        } else {
            // Switch to next player
            currentPlayerIndex = 1 - currentPlayerIndex;
        }

        return true;
    }

    /**
     * Play a complete game loop.
     */
    public void play() {
        start();
        
        while (!isGameOver()) {
            board.display();
            Player currentPlayer = getCurrentPlayer();
            Position move = currentPlayer.makeMove(board);
            makeMove(move);
        }
        
        board.display();
        System.out.println(state.getMessage());
    }

    /**
     * Get current player.
     */
    public Player getCurrentPlayer() {
        return players[currentPlayerIndex];
    }

    /**
     * Get current game state.
     */
    public GameState getState() {
        return state;
    }

    /**
     * Check if game is over.
     */
    public boolean isGameOver() {
        return state.isGameOver();
    }

    /**
     * Get the game board.
     */
    public Board getBoard() {
        return board;
    }

    /**
     * Reset the game.
     */
    public void reset() {
        board.reset();
        state = GameState.NOT_STARTED;
        currentPlayerIndex = 0;
        lastMove = null;
    }
}
