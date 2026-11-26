public class BlackjackHand extends Hand implements Comparable<BlackjackHand> {

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
