public class ConnectFourDemo {
    public static void main(String[] args) {
        Player red = new Player("Red", DiscColor.RED);
        Player yellow = new Player("Yellow", DiscColor.YELLOW);
        Game game = new Game(red, yellow);
        GameSession session = new GameSession("session-1", game);

        int botSuggestedColumn = session.getGame().suggestBotMove();
        System.out.println("Suggested column for " + session.getGame().getCurrentPlayer().getName() + ": " + botSuggestedColumn);
    }
}
