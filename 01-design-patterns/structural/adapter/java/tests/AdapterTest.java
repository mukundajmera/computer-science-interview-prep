import org.junit.jupiter.api.*;
import static org.junit.jupiter.api.Assertions.*;
import java.util.*;

/**
 * Tests for Adapter Pattern implementations
 */
public class AdapterTest {
    
    // ============ V1 Basic Tests ============
    
    @Test
    @DisplayName("VLC Adapter should implement MediaPlayer interface")
    void testVLCAdapterImplementsInterface() {
        // Given an adaptee
        VLCPlayer vlc = new VLCPlayer();
        
        // When adapted
        MediaPlayer player = new VLCPlayerAdapter(vlc);
        
        // Then should work through target interface
        assertDoesNotThrow(() -> player.play("test.vlc"));
        assertDoesNotThrow(() -> player.stop());
        assertEquals("VLC", player.getPlayerType());
    }
    
    @Test
    @DisplayName("MP4 Adapter should translate method calls correctly")
    void testMP4AdapterTranslation() {
        MediaPlayer player = new MP4PlayerAdapter();
        
        // Should translate play() to loadMP4() + startPlayback()
        assertDoesNotThrow(() -> player.play("video.mp4"));
        assertDoesNotThrow(() -> player.stop());
    }
    
    @Test
    @DisplayName("Client should work with any adapter")
    void testClientWithDifferentAdapters() {
        AudioPlayerClient client = new AudioPlayerClient();
        
        // Test with VLC
        client.setPlayer(new VLCPlayerAdapter());
        assertDoesNotThrow(() -> client.playFile("movie.vlc"));
        
        // Test with MP4
        client.setPlayer(new MP4PlayerAdapter());
        assertDoesNotThrow(() -> client.playFile("video.mp4"));
    }
    
    // ============ V2 Payment Adapter Tests ============
    
    @Test
    @DisplayName("Stripe adapter should process payments")
    void testStripeAdapter() {
        PaymentProcessor processor = new StripeAdapter(new StripeAPI());
        Map<String, String> card = Map.of(
            "number", "4111111111111111",
            "expiry", "12/25",
            "cvv", "123"
        );
        
        boolean result = processor.processPayment(99.99, "USD", card);
        assertTrue(result);
        assertEquals("Stripe", processor.getProviderName());
    }
    
    @Test
    @DisplayName("PayPal adapter should process payments")
    void testPayPalAdapter() {
        PaymentProcessor processor = new PayPalAdapter(new PayPalSDK());
        
        boolean result = processor.processPayment(49.99, "USD", Map.of());
        assertTrue(result);
        assertEquals("PayPal", processor.getProviderName());
    }
    
    @Test
    @DisplayName("Square adapter should process payments")
    void testSquareAdapter() {
        PaymentProcessor processor = new SquareAdapter(new SquareClient());
        Map<String, String> card = Map.of("number", "4111111111111111");
        
        boolean result = processor.processPayment(29.99, "USD", card);
        assertTrue(result);
        assertEquals("Square", processor.getProviderName());
    }
    
    @Test
    @DisplayName("All adapters should support refunds")
    void testRefundSupport() {
        List<PaymentProcessor> processors = List.of(
            new StripeAdapter(new StripeAPI()),
            new PayPalAdapter(new PayPalSDK()),
            new SquareAdapter(new SquareClient())
        );
        
        for (PaymentProcessor processor : processors) {
            assertTrue(processor.refund("txn_123", 10.00),
                processor.getProviderName() + " should support refunds");
        }
    }
    
    // ============ V3 Two-Way Adapter Tests ============
    
    @Test
    @DisplayName("Two-way adapter should convert XML to JSON")
    void testXmlToJsonConversion() {
        LegacyXMLDatabase xmlDb = new LegacyXMLDatabase();
        TwoWayDataAdapter adapter = new TwoWayDataAdapter(xmlDb);
        
        Map<String, Object> json = adapter.fetchAsJSON("user_1");
        
        assertFalse(json.isEmpty());
        assertEquals(1, json.get("id"));
        assertEquals("Alice", json.get("name"));
    }
    
    @Test
    @DisplayName("Two-way adapter should convert JSON to XML")
    void testJsonToXmlConversion() {
        ModernJSONAPI jsonApi = new ModernJSONAPI();
        TwoWayDataAdapter adapter = new TwoWayDataAdapter(jsonApi);
        
        String xml = adapter.fetchAsXML("product_1");
        
        assertTrue(xml.contains("<id>1</id>"));
        assertTrue(xml.contains("<name>Laptop</name>"));
    }
    
    @Test
    @DisplayName("Two-way adapter should save JSON to XML system")
    void testSaveJsonToXmlSystem() {
        LegacyXMLDatabase xmlDb = new LegacyXMLDatabase();
        TwoWayDataAdapter adapter = new TwoWayDataAdapter(xmlDb);
        
        Map<String, Object> newUser = Map.of(
            "id", 99,
            "name", "Test",
            "email", "test@test.com"
        );
        
        adapter.saveFromJSON(newUser);
        
        String saved = xmlDb.fetchAsXML("user_99");
        assertTrue(saved.contains("<id>99</id>"));
    }
    
    // ============ Edge Case Tests ============
    
    @Test
    @DisplayName("Adapter should handle null adaptee gracefully")
    void testNullHandling() {
        // This tests that we properly handle edge cases
        TwoWayDataAdapter adapter = new TwoWayDataAdapter((XMLDataSource) null);
        
        // Should throw or return empty, not crash unexpectedly
        assertThrows(NullPointerException.class, () -> adapter.fetchAsXML("test"));
    }
    
    @Test
    @DisplayName("Adapter should handle empty data")
    void testEmptyDataHandling() {
        LegacyXMLDatabase xmlDb = new LegacyXMLDatabase();
        TwoWayDataAdapter adapter = new TwoWayDataAdapter(xmlDb);
        
        Map<String, Object> result = adapter.fetchAsJSON("nonexistent");
        assertTrue(result.isEmpty());
    }
}
