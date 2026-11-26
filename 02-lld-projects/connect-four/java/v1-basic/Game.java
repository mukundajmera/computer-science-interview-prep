public class Game {
    private final Board board;
    private final Player player1;
    private final Player player2;
    private Player currentPlayer;
    private GameState state;
    private Player winner;

    public Game(Player player1, Player player2) {
        this(player1, player2, new Board());
    }

    public Game(Player player1, Player player2, Board board) {
        this.player1 = player1;
        this.player2 = player2;
        this.board = board;
        this.currentPlayer = player1;
        this.state = GameState.IN_PROGRESS;
        this.winner = null;
    }

    public boolean makeMove(Player player, int column) {
        if (state.isTerminal()) {
            return false;
        }
        if (player == null || player != currentPlayer) {
            return false;
        }
        if (!board.canPlace(column)) {
            return false;
        }

        int row = board.placeDisc(column, player.getColor());
        if (row < 0) {
            return false;
        }

        if (board.checkWin(row, column, player.getColor())) {
            winner = player;
            state = player.getColor() == DiscColor.RED ? GameState.RED_WON : GameState.YELLOW_WON;
            return true;
        }

        if (board.isFull()) {
            state = GameState.DRAW;
            return true;
        }

        currentPlayer = (currentPlayer == player1) ? player2 : player1;
        return true;
    }

    public Player getCurrentPlayer() {
        return currentPlayer;
    }

    public GameState getGameState() {
        return state;
    }

    public Player getWinner() {
        return winner;
    }

    public Board getBoard() {
        return board;
    }
}
