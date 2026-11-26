public class BlackjackHand extends Hand {

    public int getScore() {
        int score = 0;
        int aceCount = 0;

        for (Card card : cards) {
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

    public boolean isBust() {
        return getScore() > 21;
    }

    public boolean isBlackjack() {
        return cards.size() == 2 && getScore() == 21;
    }
}
