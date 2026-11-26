import java.util.ArrayList;
import java.util.List;

public class BlackjackGame {
    private final Deck deck;
    private final List<Player> players;
    private final BlackjackHand dealerHand;
    private GameState state;

    public BlackjackGame() {
        this.deck = new Deck();
        this.players = new ArrayList<>();
        this.dealerHand = new BlackjackHand();
        this.state = GameState.BETTING;
    }

    public void addPlayer(Player player) {
        players.add(player);
    }

    public void startRound() {
        if (state != GameState.BETTING) {
            throw new IllegalStateException("Must be in BETTING state to start round.");
        }

        deck.shuffle();
        for (Player p : players) {
            p.getHand().clear();
        }
        dealerHand.clear();

        state = GameState.DEALING;
        for (int i = 0; i < 2; i++) {
            for (Player p : players) {
                p.getHand().addCard(deck.dealCard());
            }
            dealerHand.addCard(deck.dealCard());
        }
        state = GameState.PLAYER_TURNS;
    }

    public void hit(Player p) {
        if (state != GameState.PLAYER_TURNS) {
            throw new IllegalStateException("Not currently in player turns phase.");
        }
        if (p.getHand().isBust()) return;
        p.getHand().addCard(deck.dealCard());
    }

    public void stand(Player p) {
        if (state != GameState.PLAYER_TURNS) {
            throw new IllegalStateException("Not currently in player turns phase.");
        }
        // Logic to advance to next player could be here
    }

    public void doubleDown(Player p) {
        if (state != GameState.PLAYER_TURNS) {
            throw new IllegalStateException("Not currently in player turns phase.");
        }
        if (p.getHand().getCards().size() != 2) {
            throw new IllegalStateException("Can only double down on initial two cards.");
        }
        p.doubleBet();
        p.getHand().addCard(deck.dealCard());
    }

    public void advanceToDealer() {
        state = GameState.DEALER_TURN;
    }

    public void playDealerTurn() {
        if (state != GameState.DEALER_TURN) {
            state = GameState.DEALER_TURN;
        }
        while (dealerHand.getScore() < 17) {
            dealerHand.addCard(deck.dealCard());
        }
        state = GameState.SETTLEMENT;
    }

    public void settleBets() {
        if (state != GameState.SETTLEMENT) {
            state = GameState.SETTLEMENT;
        }

        int dealerScore = dealerHand.getScore();
        boolean dealerBust = dealerHand.isBust();
        boolean dealerBlackjack = dealerHand.isBlackjack();

        for (Player p : players) {
            BlackjackHand playerHand = p.getHand();
            if (playerHand.isBust()) {
                // Player lost, balance already deducted when bet placed
            } else if (playerHand.isBlackjack()) {
                if (dealerBlackjack) {
                    p.pushBet(); // Tie
                } else {
                    p.receiveWinnings(2.5); // 3:2 payout (bet + 1.5 * bet)
                }
            } else if (dealerBust) {
                p.receiveWinnings(2.0); // 1:1 payout (bet + 1 * bet)
            } else if (dealerBlackjack) {
                // Player lost
            } else {
                int playerScore = playerHand.getScore();
                if (playerScore > dealerScore) {
                    p.receiveWinnings(2.0);
                } else if (playerScore == dealerScore) {
                    p.pushBet();
                } else {
                    // Player lost
                }
            }
            p.resetBet();
        }
        state = GameState.BETTING;
    }
    
    public BlackjackHand getDealerHand() {
        return dealerHand;
    }
}
