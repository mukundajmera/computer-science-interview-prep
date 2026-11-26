import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

import java.util.List;

public class BlackjackV3Test {

    @Test
    public void testSplitMechanic() {
        Player player = new Player("Alice", 100);
        player.placeBet(10, 0);
        
        BlackjackHand hand = player.getHands().get(0);
        hand.addCard(new Card(Suit.HEARTS, Rank.EIGHT));
        hand.addCard(new Card(Suit.CLUBS, Rank.EIGHT));
        
        assertTrue(hand.canSplit());
        
        BlackjackGame game = new BlackjackGame();
        game.addPlayer(player);
        game.state = GameState.PLAYER_TURNS;
        
        game.split(player, 0);
        
        assertEquals(2, player.getHands().size());
        assertEquals(80.0, player.getBalance());
        assertEquals(10.0, player.getHands().get(0).getBet());
        assertEquals(10.0, player.getHands().get(1).getBet());
        assertEquals(2, player.getHands().get(0).getCards().size());
        assertEquals(2, player.getHands().get(1).getCards().size());
    }

    @Test
    public void testDoubleDownMechanic() {
        Player player = new Player("Bob", 100);
        player.placeBet(10, 0);
        
        BlackjackHand hand = player.getHands().get(0);
        hand.addCard(new Card(Suit.HEARTS, Rank.FIVE));
        hand.addCard(new Card(Suit.CLUBS, Rank.SIX));
        
        BlackjackGame game = new BlackjackGame();
        game.addPlayer(player);
        
        game.state = GameState.PLAYER_TURNS;
        
        // Mock dealer hand so we don't draw forever
        BlackjackHand mockDealer = new BlackjackHand();
        mockDealer.addCard(new Card(Suit.HEARTS, Rank.TEN));
        mockDealer.addCard(new Card(Suit.CLUBS, Rank.EIGHT));
        game.dealerHand = mockDealer;
        
        game.doubleDown(player, 0);
        
        assertEquals(3, player.getHands().get(0).getCards().size());
        assertTrue(player.getHands().get(0).hasDoubled());
    }

    @Test
    public void testInsuranceMechanic() {
        Player player = new Player("Charlie", 100);
        player.placeBet(10, 0);
        
        BlackjackGame game = new BlackjackGame();
        game.addPlayer(player);
        
        game.state = GameState.INSURANCE;
        
        BlackjackHand mockDealer = new BlackjackHand();
        mockDealer.addCard(new Card(Suit.HEARTS, Rank.ACE));
        mockDealer.addCard(new Card(Suit.CLUBS, Rank.TEN));
        game.dealerHand = mockDealer;
        
        game.offerInsurance(player, 5);
        
        assertEquals(85.0, player.getBalance());
        assertEquals(5.0, player.getInsuranceBet());
        
        game.closeInsurance();
        
        assertEquals(100.0, player.getBalance());
        assertEquals(GameState.BETTING, game.state);
    }
    
    @Test
    public void testPayoutCalculations() {
        Player player = new Player("Dave", 100);
        player.placeBet(10, 0);
        
        BlackjackGame game = new BlackjackGame();
        game.addPlayer(player);
        
        game.state = GameState.SETTLEMENT;
        
        BlackjackHand mockDealer = new BlackjackHand();
        mockDealer.addCard(new Card(Suit.SPADES, Rank.TEN));
        mockDealer.addCard(new Card(Suit.DIAMONDS, Rank.EIGHT));
        game.dealerHand = mockDealer;
        
        player.getHands().get(0).addCard(new Card(Suit.HEARTS, Rank.TEN));
        player.getHands().get(0).addCard(new Card(Suit.CLUBS, Rank.NINE)); // 19 vs 18
        
        game.settleBets();
        assertEquals(110.0, player.getBalance());
    }

    @Test
    public void testMultiPlayerStateMachine() {
        Player p1 = new Player("P1", 100);
        Player p2 = new Player("P2", 100);
        
        p1.placeBet(10, 0);
        p2.placeBet(10, 0);
        
        BlackjackGame game = new BlackjackGame();
        game.addPlayer(p1);
        game.addPlayer(p2);
        
        game.state = GameState.PLAYER_TURNS;
        
        BlackjackHand mockDealer = new BlackjackHand();
        mockDealer.addCard(new Card(Suit.SPADES, Rank.TEN));
        mockDealer.addCard(new Card(Suit.DIAMONDS, Rank.EIGHT));
        game.dealerHand = mockDealer;
        
        p1.getHands().get(0).addCard(new Card(Suit.HEARTS, Rank.TEN));
        p1.getHands().get(0).addCard(new Card(Suit.CLUBS, Rank.NINE));
        p1.getHands().get(0).addCard(new Card(Suit.DIAMONDS, Rank.NINE)); // bust
        
        p2.getHands().get(0).addCard(new Card(Suit.HEARTS, Rank.TEN));
        p2.getHands().get(0).addCard(new Card(Suit.CLUBS, Rank.NINE));
        
        // Use reflection to call advanceIfNeeded
        try {
            java.lang.reflect.Method advance = BlackjackGame.class.getDeclaredMethod("advanceIfNeeded");
            advance.setAccessible(true);
            advance.invoke(game);
        } catch (Exception e) {}
        
        assertEquals(1, game.currentPlayerIndex);
        
        game.stand(p2, 0);
        
        assertEquals(GameState.BETTING, game.state);
    }
}
