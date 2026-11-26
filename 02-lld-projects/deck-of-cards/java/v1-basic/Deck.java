import java.util.ArrayList;
import java.util.Collections;
import java.util.List;

public class Deck {
    private final List<Card> cards;
    private int dealIndex;

    public Deck() {
        cards = new ArrayList<>();
        for (Suit suit : Suit.values()) {
            for (Rank rank : Rank.values()) {
                cards.add(new Card(suit, rank));
            }
        }
        dealIndex = 0;
    }

    public void shuffle() {
        Collections.shuffle(cards);
        dealIndex = 0;
    }

    public Card dealCard() {
        if (dealIndex >= cards.size()) {
            throw new IllegalStateException("No cards left in the deck.");
        }
        return cards.get(dealIndex++);
    }

    public int remainingCards() {
        return cards.size() - dealIndex;
    }
}
