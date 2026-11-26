import org.junit.jupiter.api.*;
import static org.junit.jupiter.api.Assertions.*;

/**
 * Tests for Decorator Pattern implementations
 */
public class DecoratorTest {
    
    // ============ V1 Coffee Shop Tests ============
    
    @Test
    @DisplayName("Espresso should have base cost")
    void testEspressoBaseCost() {
        Beverage espresso = new Espresso();
        assertEquals(1.99, espresso.cost(), 0.01);
        assertEquals("Espresso", espresso.getDescription());
    }
    
    @Test
    @DisplayName("Single decorator should add cost and description")
    void testSingleDecorator() {
        Beverage beverage = new Espresso();
        beverage = new Milk(beverage);
        
        assertEquals(2.29, beverage.cost(), 0.01);  // 1.99 + 0.30
        assertTrue(beverage.getDescription().contains("Milk"));
    }
    
    @Test
    @DisplayName("Multiple decorators should stack correctly")
    void testStackedDecorators() {
        Beverage beverage = new DarkRoast();  // 1.49
        beverage = new Mocha(beverage);        // +0.50
        beverage = new Mocha(beverage);        // +0.50
        beverage = new Whip(beverage);         // +0.40
        
        assertEquals(2.89, beverage.cost(), 0.01);
        assertTrue(beverage.getDescription().contains("Dark Roast"));
        // Should have Mocha twice
        String desc = beverage.getDescription();
        assertEquals(2, desc.split("Mocha").length - 1);
    }
    
    @Test
    @DisplayName("Order of decorators should not affect total cost")
    void testDecoratorOrder() {
        // Order 1: Milk then Mocha
        Beverage order1 = new Espresso();
        order1 = new Milk(order1);
        order1 = new Mocha(order1);
        
        // Order 2: Mocha then Milk
        Beverage order2 = new Espresso();
        order2 = new Mocha(order2);
        order2 = new Milk(order2);
        
        assertEquals(order1.cost(), order2.cost(), 0.01);
    }
    
    // ============ V2 Data Stream Tests ============
    
    @Test
    @DisplayName("Plain data source should read/write correctly")
    void testPlainDataSource() throws Exception {
        String testFile = "test_decorator.txt";
        String testData = "Hello World";
        
        DataSource source = new FileDataSource(testFile);
        source.writeData(testData);
        String read = source.readData();
        
        assertEquals(testData, read);
        new java.io.File(testFile).delete();
    }
    
    @Test
    @DisplayName("Encryption decorator should encrypt and decrypt")
    void testEncryptionDecorator() throws Exception {
        String testFile = "test_encrypted.txt";
        String testData = "Secret Message";
        
        DataSource source = new EncryptionDecorator(new FileDataSource(testFile));
        source.writeData(testData);
        
        // Read raw file - should be different
        DataSource rawSource = new FileDataSource(testFile);
        String rawData = rawSource.readData();
        assertNotEquals(testData, rawData);
        
        // Read through decorator - should be original
        String decrypted = source.readData();
        assertEquals(testData, decrypted);
        
        new java.io.File(testFile).delete();
    }
    
    @Test
    @DisplayName("Stacked decorators should work together")
    void testStackedDataDecorators() throws Exception {
        String testFile = "test_stacked.txt";
        String testData = "Complex data with special chars: !@#$%";
        
        DataSource source = new LoggingDecorator(
            new CompressionDecorator(
                new EncryptionDecorator(
                    new FileDataSource(testFile)
                )
            )
        );
        
        source.writeData(testData);
        String result = source.readData();
        
        assertEquals(testData, result);
        new java.io.File(testFile).delete();
    }
    
    // ============ V3 Middleware Tests ============
    
    @Test
    @DisplayName("Application handler should return correct response")
    void testApplicationHandler() {
        RequestHandler handler = new ApplicationHandler();
        HttpRequest request = new HttpRequest("GET", "/api/users");
        
        HttpResponse response = handler.handle(request);
        
        assertEquals(200, response.getStatusCode());
        assertTrue(response.getBody().contains("users"));
    }
    
    @Test
    @DisplayName("Authentication middleware should set user attribute")
    void testAuthenticationMiddleware() {
        RequestHandler handler = new AuthenticationMiddleware(new ApplicationHandler());
        HttpRequest request = new HttpRequest("GET", "/api/protected");
        request.setHeader("Authorization", "Bearer valid-token-123");
        
        handler.handle(request);
        
        assertEquals("AuthenticatedUser", request.getAttribute("user"));
    }
    
    @Test
    @DisplayName("Rate limit middleware should block after max requests")
    void testRateLimitMiddleware() {
        RequestHandler handler = new RateLimitMiddleware(new ApplicationHandler());
        
        // First 5 requests should succeed
        for (int i = 0; i < 5; i++) {
            HttpRequest request = new HttpRequest("GET", "/api/users");
            request.setHeader("X-Client-IP", "192.168.1.100");
            HttpResponse response = handler.handle(request);
            assertEquals(200, response.getStatusCode());
        }
        
        // 6th request should be rate limited
        HttpRequest request = new HttpRequest("GET", "/api/users");
        request.setHeader("X-Client-IP", "192.168.1.100");
        HttpResponse response = handler.handle(request);
        assertEquals(429, response.getStatusCode());
    }
    
    @Test
    @DisplayName("Caching middleware should cache GET requests")
    void testCachingMiddleware() {
        RequestHandler handler = new CachingMiddleware(new ApplicationHandler());
        HttpRequest request1 = new HttpRequest("GET", "/api/users");
        
        // First request - cache miss
        HttpResponse response1 = handler.handle(request1);
        assertEquals("MISS", response1.getHeader("X-Cache"));
        
        // Second request - cache hit
        HttpRequest request2 = new HttpRequest("GET", "/api/users");
        HttpResponse response2 = handler.handle(request2);
        assertEquals("HIT", response2.getHeader("X-Cache"));
    }
}
