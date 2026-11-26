public class BlackjackHand extends Hand implements Comparable<BlackjackHand> {
    private double bet;
    private boolean isStand;
    private boolean hasDoubled;

    public BlackjackHand() {
        this(0.0);
    }
    
    public BlackjackHand(double bet) {
        this.bet = bet;
        this.isStand = false;
        this.hasDoubled = false;
    }

    public double getBet() {
        return bet;
    }
    
    public void setBet(double bet) {
        this.bet = bet;
    }
    
    public void addBet(double amount) {
        this.bet += amount;
    }

    public boolean isStand() {
        return isStand;
    }

    public void setStand(boolean stand) {
        isStand = stand;
    }

    public boolean hasDoubled() {
        return hasDoubled;
    }

    public void setDoubled(boolean doubled) {
        hasDoubled = doubled;
    }

    public int getScore() {
        int score = 0;
        int aceCount = 0;

        for (Card card : getCards()) {
            int value = card.getRank().getValue();
            if (card.getRank() == Rank.ACE) {
                aceCount++;
                score += 11;
            } else {
                score += value;
            }
        }

        while (score > 21 && aceCount > 0) {
            score -= 10;
            aceCount--;
        }

        return score;
    }

    public boolean isSoft() {
        int score = 0;
        int aceCount = 0;

        for (Card card : getCards()) {
            int value = card.getRank().getValue();
            if (card.getRank() == Rank.ACE) {
                aceCount++;
                score += 11;
            } else {
                score += value;
            }
        }

        while (score > 21 && aceCount > 0) {
            score -= 10;
            aceCount--;
        }

        return aceCount > 0;
    }

    public boolean isBust() {
        return getScore() > 21;
    }

    public boolean isBlackjack() {
        return getCards().size() == 2 && getScore() == 21;
    }

    public boolean canSplit() {
        return getCards().size() == 2 && 
               getCards().get(0).getRank().getValue() == getCards().get(1).getRank().getValue();
    }

    private double getCompareValue() {
        if (isBust()) return -1;
        if (isBlackjack()) return 22;
        return getScore();
    }

    @Override
    public int compareTo(BlackjackHand other) {
        return Double.compare(this.getCompareValue(), other.getCompareValue());
    }
}
