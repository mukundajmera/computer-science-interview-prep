import java.util.ArrayList;
import java.util.List;

public class BlackjackGame {
    public Deck deck; // Public for testing
    private final List<Player> players;
    public BlackjackHand dealerHand; // Public for testing
    public GameState state; // Public for testing
    public int currentPlayerIndex; // Public for testing
    private int currentHandIndex;

    public BlackjackGame() {
        this.deck = new Deck();
        this.players = new ArrayList<>();
        this.dealerHand = new BlackjackHand();
        this.state = GameState.BETTING;
        this.currentPlayerIndex = 0;
        this.currentHandIndex = 0;
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
            p.clearHands();
        }
        dealerHand.clear();

        state = GameState.DEALING;
        for (int i = 0; i < 2; i++) {
            for (Player p : players) {
                p.getHands().get(0).addCard(deck.dealCard());
            }
            dealerHand.addCard(deck.dealCard());
        }
        
        if (dealerHand.getCards().get(0).getRank() == Rank.ACE) {
            state = GameState.INSURANCE;
        } else {
            state = GameState.PLAYER_TURNS;
        }
        
        currentPlayerIndex = 0;
        currentHandIndex = 0;
        advanceIfNeeded();
    }
    
    public void offerInsurance(Player player, double amount) {
        if (state != GameState.INSURANCE) {
            throw new IllegalStateException("Not currently in insurance phase.");
        }
        player.placeInsuranceBet(amount);
    }
    
    public void closeInsurance() {
        if (state != GameState.INSURANCE) {
            throw new IllegalStateException("Not currently in insurance phase.");
        }
        
        if (dealerHand.isBlackjack()) {
            for (Player p : players) {
                if (p.getInsuranceBet() > 0) {
                    p.winInsurance();
                }
            }
            state = GameState.SETTLEMENT;
            settleBets();
        } else {
            for (Player p : players) {
                p.clearInsuranceBet();
            }
            state = GameState.PLAYER_TURNS;
            advanceIfNeeded();
        }
    }

    public void hit(Player p, int handIndex) {
        if (state != GameState.PLAYER_TURNS) {
            throw new IllegalStateException("Not currently in player turns phase.");
        }
        if (p != players.get(currentPlayerIndex) || handIndex != currentHandIndex) {
            throw new IllegalArgumentException("Not this player's/hand's turn.");
        }
        
        BlackjackHand hand = p.getHands().get(handIndex);
        if (hand.isBust() || hand.isStand() || hand.hasDoubled()) return;
        
        hand.addCard(deck.dealCard());
        advanceIfNeeded();
    }

    public void stand(Player p, int handIndex) {
        if (state != GameState.PLAYER_TURNS) {
            throw new IllegalStateException("Not currently in player turns phase.");
        }
        if (p != players.get(currentPlayerIndex) || handIndex != currentHandIndex) {
            throw new IllegalArgumentException("Not this player's/hand's turn.");
        }
        
        p.getHands().get(handIndex).setStand(true);
        advanceToNextHand();
    }

    public void doubleDown(Player p, int handIndex) {
        if (state != GameState.PLAYER_TURNS) {
            throw new IllegalStateException("Not currently in player turns phase.");
        }
        if (p != players.get(currentPlayerIndex) || handIndex != currentHandIndex) {
            throw new IllegalArgumentException("Not this player's/hand's turn.");
        }
        
        BlackjackHand hand = p.getHands().get(handIndex);
        if (hand.getCards().size() != 2) {
            throw new IllegalStateException("Can only double down on initial two cards.");
        }
        p.doubleBet(handIndex);
        hand.setDoubled(true);
        hand.addCard(deck.dealCard());
        advanceToNextHand();
    }
    
    public void split(Player p, int handIndex) {
        if (state != GameState.PLAYER_TURNS) {
            throw new IllegalStateException("Not currently in player turns phase.");
        }
        if (p != players.get(currentPlayerIndex) || handIndex != currentHandIndex) {
            throw new IllegalArgumentException("Not this player's/hand's turn.");
        }
        
        BlackjackHand hand = p.getHands().get(handIndex);
        if (!hand.canSplit()) {
            throw new IllegalStateException("Cannot split this hand.");
        }
        
        Card cardToMove = hand.getCards().remove(1);
        BlackjackHand newHand = p.addSplitHand(hand.getBet());
        newHand.addCard(cardToMove);
        
        hand.addCard(deck.dealCard());
        newHand.addCard(deck.dealCard());
        
        advanceIfNeeded();
    }
    
    private void advanceIfNeeded() {
        if (state != GameState.PLAYER_TURNS) return;
        
        while (currentPlayerIndex < players.size()) {
            Player p = players.get(currentPlayerIndex);
            if (currentHandIndex < p.getHands().size()) {
                BlackjackHand hand = p.getHands().get(currentHandIndex);
                if (hand.isBust() || hand.isStand() || hand.hasDoubled() || hand.isBlackjack()) {
                    currentHandIndex++;
                } else {
                    return; // Still active
                }
            } else {
                currentPlayerIndex++;
                currentHandIndex = 0;
            }
        }
        
        playDealerTurn();
    }
    
    private void advanceToNextHand() {
        currentHandIndex++;
        advanceIfNeeded();
    }

    public void playDealerTurn() {
        state = GameState.DEALER_TURN;
        
        while (true) {
            int score = dealerHand.getScore();
            if (score < 17 || (score == 17 && dealerHand.isSoft())) {
                dealerHand.addCard(deck.dealCard());
            } else {
                break;
            }
        }
        settleBets();
    }

    public void settleBets() {
        state = GameState.SETTLEMENT;

        for (Player p : players) {
            for (int i = 0; i < p.getHands().size(); i++) {
                BlackjackHand playerHand = p.getHands().get(i);
                if (playerHand.getBet() == 0) continue;
                
                if (playerHand.isBust()) {
                    // Lost
                } else if (playerHand.isBlackjack()) {
                    if (dealerHand.isBlackjack()) {
                        p.pushBet(i); // Tie
                    } else {
                        p.receiveWinnings(2.5, i); // 3:2 payout
                    }
                } else if (dealerHand.isBust()) {
                    p.receiveWinnings(2.0, i); // 1:1 payout
                } else if (dealerHand.isBlackjack()) {
                    // Lost
                } else {
                    int cmp = playerHand.compareTo(dealerHand);
                    if (cmp > 0) {
                        p.receiveWinnings(2.0, i);
                    } else if (cmp == 0) {
                        p.pushBet(i);
                    } else {
                        // Lost
                    }
                }
                playerHand.setBet(0.0);
            }
        }
        state = GameState.BETTING;
    }
    
    public BlackjackHand getDealerHand() {
        return dealerHand;
    }
}
