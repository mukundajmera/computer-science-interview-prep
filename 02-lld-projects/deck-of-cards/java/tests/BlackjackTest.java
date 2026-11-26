import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

public class BlackjackTest {

    @Test
    public void testSoft17Detection() {
        BlackjackHand hand = new BlackjackHand();
        hand.addCard(new Card(Suit.HEARTS, Rank.ACE));
        hand.addCard(new Card(Suit.CLUBS, Rank.SIX));
        
        assertEquals(17, hand.getScore());
        assertTrue(hand.isSoft());
    }

    @Test
    public void testHard17Detection() {
        BlackjackHand hand = new BlackjackHand();
        hand.addCard(new Card(Suit.HEARTS, Rank.TEN));
        hand.addCard(new Card(Suit.CLUBS, Rank.SEVEN));
        
        assertEquals(17, hand.getScore());
        assertFalse(hand.isSoft());
    }

    @Test
    public void testSoftToHardConversion() {
        BlackjackHand hand = new BlackjackHand();
        hand.addCard(new Card(Suit.HEARTS, Rank.ACE));
        hand.addCard(new Card(Suit.CLUBS, Rank.SIX));
        
        assertEquals(17, hand.getScore());
        assertTrue(hand.isSoft());
        
        hand.addCard(new Card(Suit.SPADES, Rank.TEN));
        assertEquals(17, hand.getScore());
        assertFalse(hand.isSoft());
    }

    @Test
    public void testHandComparison() {
        BlackjackHand hand1 = new BlackjackHand();
        hand1.addCard(new Card(Suit.HEARTS, Rank.TEN));
        hand1.addCard(new Card(Suit.CLUBS, Rank.NINE)); // 19
        
        BlackjackHand hand2 = new BlackjackHand();
        hand2.addCard(new Card(Suit.HEARTS, Rank.TEN));
        hand2.addCard(new Card(Suit.CLUBS, Rank.EIGHT)); // 18
        
        assertTrue(hand1.compareTo(hand2) > 0);
        assertTrue(hand2.compareTo(hand1) < 0);
        
        BlackjackHand hand3 = new BlackjackHand();
        hand3.addCard(new Card(Suit.HEARTS, Rank.TEN));
        hand3.addCard(new Card(Suit.CLUBS, Rank.NINE)); // 19
        
        assertEquals(0, hand1.compareTo(hand3));
    }

    @Test
    public void testBlackjackBeats21() {
        BlackjackHand bjHand = new BlackjackHand();
        bjHand.addCard(new Card(Suit.HEARTS, Rank.ACE));
        bjHand.addCard(new Card(Suit.CLUBS, Rank.TEN)); // 21 (Blackjack)
        
        BlackjackHand reg21 = new BlackjackHand();
        reg21.addCard(new Card(Suit.HEARTS, Rank.TEN));
        reg21.addCard(new Card(Suit.CLUBS, Rank.SIX));
        reg21.addCard(new Card(Suit.SPADES, Rank.FIVE)); // 21 (Not Blackjack)
        
        assertTrue(bjHand.compareTo(reg21) > 0);
        assertTrue(reg21.compareTo(bjHand) < 0);
    }
}
