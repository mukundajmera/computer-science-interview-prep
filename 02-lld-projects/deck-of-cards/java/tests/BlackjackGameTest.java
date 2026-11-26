import org.junit.jupiter.api.Test;
import java.util.HashSet;
import java.util.Set;
import static org.junit.jupiter.api.Assertions.*;

public class BlackjackGameTest {

    @Test
    public void testDeckCreationAndShuffleRandomness() {
        Deck deck1 = new Deck();
        Deck deck2 = new Deck();
        
        assertEquals(52, deck1.remainingCards());
        
        Set<String> cards = new HashSet<>();
        while(deck1.remainingCards() > 0) {
            cards.add(deck1.dealCard().toString());
        }
        assertEquals(52, cards.size());
        
        // Ensure shuffle changes order (with high probability)
        deck2.shuffle();
        Deck deck3 = new Deck();
        boolean differs = false;
        for (int i=0; i<52; i++) {
            if (!deck2.dealCard().toString().equals(deck3.dealCard().toString())) {
                differs = true;
                break;
            }
        }
        assertTrue(differs, "Shuffled deck should differ from unshuffled deck");
    }

    @Test
    public void testDynamicAceScoreResolution() {
        BlackjackHand hand = new BlackjackHand();
        
        // Soft 21: Ace + 10
        hand.addCard(new Card(Suit.SPADES, Rank.ACE));
        hand.addCard(new Card(Suit.HEARTS, Rank.KING));
        assertEquals(21, hand.getScore());
        assertTrue(hand.isBlackjack());
        
        // Multi Ace: Ace + Ace + 9 = 21
        hand.clear();
        hand.addCard(new Card(Suit.SPADES, Rank.ACE));
        hand.addCard(new Card(Suit.HEARTS, Rank.ACE));
        hand.addCard(new Card(Suit.CLUBS, Rank.NINE));
        assertEquals(21, hand.getScore());
        assertFalse(hand.isBlackjack());
        
        // Hard hand that would bust if Ace was 11: 10 + 5 + Ace = 16
        hand.clear();
        hand.addCard(new Card(Suit.SPADES, Rank.KING));
        hand.addCard(new Card(Suit.HEARTS, Rank.FIVE));
        hand.addCard(new Card(Suit.CLUBS, Rank.ACE));
        assertEquals(16, hand.getScore());
        
        // 4 Aces
        hand.clear();
        hand.addCard(new Card(Suit.SPADES, Rank.ACE));
        hand.addCard(new Card(Suit.HEARTS, Rank.ACE));
        hand.addCard(new Card(Suit.CLUBS, Rank.ACE));
        hand.addCard(new Card(Suit.DIAMONDS, Rank.ACE));
        assertEquals(14, hand.getScore()); // 11 + 1 + 1 + 1
    }

    @Test
    public void testNaturalBlackjackDetection() {
        BlackjackHand hand = new BlackjackHand();
        hand.addCard(new Card(Suit.SPADES, Rank.ACE));
        hand.addCard(new Card(Suit.HEARTS, Rank.JACK));
        assertTrue(hand.isBlackjack());
        
        hand.clear();
        hand.addCard(new Card(Suit.SPADES, Rank.ACE));
        hand.addCard(new Card(Suit.HEARTS, Rank.NINE));
        assertFalse(hand.isBlackjack());
        
        hand.clear();
        hand.addCard(new Card(Suit.SPADES, Rank.TEN));
        hand.addCard(new Card(Suit.HEARTS, Rank.FIVE));
        hand.addCard(new Card(Suit.CLUBS, Rank.SIX));
        assertEquals(21, hand.getScore());
        assertFalse(hand.isBlackjack()); // Not 2 cards
    }

    @Test
    public void testCompleteRoundSimulationDealerDrawing() {
        BlackjackGame game = new BlackjackGame();
        Player p1 = new Player("Bob", 1000);
        game.addPlayer(p1);
        
        p1.placeBet(100);
        game.startRound();
        
        assertEquals(900, p1.getBalance());
        assertEquals(2, p1.getHand().getCards().size());
        assertEquals(2, game.getDealerHand().getCards().size());
        
        game.playDealerTurn();
        assertTrue(game.getDealerHand().getScore() >= 17);
        
        game.settleBets();
        // Since it's random, we can't assert exact balance, but we can assert it was handled
        assertTrue(p1.getBalance() >= 900); // Could be 900, 1000, 1100, 1150
    }
}
