public class ConnectFourDemo {
    public static void main(String[] args) {
        Player red = new Player("Red", DiscColor.RED);
        Player yellow = new Player("Yellow", DiscColor.YELLOW);
        Game game = new Game(red, yellow);

        game.makeMove(red, 0);
        game.makeMove(yellow, 1);
        game.makeMove(red, 0);
        game.makeMove(yellow, 1);
        game.makeMove(red, 0);
        game.makeMove(yellow, 1);
        game.makeMove(red, 0);

        System.out.println("State: " + game.getGameState());
        System.out.println("Winner: " + (game.getWinner() == null ? "None" : game.getWinner().getName()));
    }
}
