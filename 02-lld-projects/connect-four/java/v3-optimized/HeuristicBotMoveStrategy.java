public class HeuristicBotMoveStrategy implements BotMoveStrategy {
    @Override
    public int selectColumn(Board board, DiscColor botColor) {
        DiscColor opponent = botColor.opposite();

        // Winning move if available.
        for (int col = 0; col < board.getCols(); col++) {
            if (isWinningMove(board, col, botColor)) {
                return col;
            }
        }

        // Block opponent winning move.
        for (int col = 0; col < board.getCols(); col++) {
            if (isWinningMove(board, col, opponent)) {
                return col;
            }
        }

        // Deterministic fallback: first legal column.
        for (int col = 0; col < board.getCols(); col++) {
            if (board.canPlace(col)) {
                return col;
            }
        }
        return -1;
    }

    private boolean isWinningMove(Board board, int col, DiscColor color) {
        if (!board.canPlace(col)) {
            return false;
        }
        int row = board.placeDisc(col, color);
        if (row < 0) {
            return false;
        }
        boolean win = board.checkWin(row, col, color);
        board.clearCell(row, col);
        return win;
    }
}
