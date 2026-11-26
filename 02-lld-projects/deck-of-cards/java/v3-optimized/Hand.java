import java.util.ArrayList;
import java.util.List;
import java.util.Collections;

public class Hand {
    protected final List<Card> cards;

    public Hand() {
        cards = new ArrayList<>();
    }

    public void addCard(Card card) {
        cards.add(card);
    }

    public List<Card> getCards() {
        return cards;
    }
    
    public List<Card> getCardsReadOnly() {
        return Collections.unmodifiableList(cards);
    }

    public void clear() {
        cards.clear();
    }
}
