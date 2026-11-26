public class BlackjackDemo {
    public static void main(String[] args) {
        BlackjackGame game = new BlackjackGame();
        Player p1 = new Player("Alice", 1000);
        game.addPlayer(p1);

        p1.placeBet(100, 0);
        game.startRound();

        System.out.println("Alice's Hand: " + p1.getHands().get(0).getCards() + " (Score: " + p1.getHands().get(0).getScore() + ")");
        System.out.println("Dealer's Face Up Card: " + game.getDealerHand().getCards().get(0));

        // Basic simulation: Player stands immediately
        game.playDealerTurn();
        System.out.println("Dealer's Hand: " + game.getDealerHand().getCards() + " (Score: " + game.getDealerHand().getScore() + ")");

        game.settleBets();
        System.out.println("Alice's Balance: " + p1.getBalance());
    }
}
