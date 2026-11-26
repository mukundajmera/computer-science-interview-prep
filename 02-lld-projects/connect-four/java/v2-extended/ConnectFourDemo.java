public class ConnectFourDemo {
    public static void main(String[] args) {
        Player red = new Player("Red", DiscColor.RED);
        Player yellow = new Player("Yellow", DiscColor.YELLOW);
        Game game = new Game(red, yellow, new Board(6, 7));

        game.makeMove(red, 0);
        game.makeMove(yellow, 1);
        game.makeMove(red, 0);

        System.out.println("History size before undo: " + game.getMoveHistory().size());
        game.undoLastMove();
        System.out.println("History size after undo: " + game.getMoveHistory().size());
        System.out.println("Current player: " + game.getCurrentPlayer().getName());
    }
}
