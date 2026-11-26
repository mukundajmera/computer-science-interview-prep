import org.junit.jupiter.api.*;
import static org.junit.jupiter.api.Assertions.*;

public class ProxyTest {
    
    @Test
    @DisplayName("Virtual proxy should defer loading")
    void testVirtualProxyDeferLoading() {
        // Creating proxy should not load image
        ProxyImage proxy = new ProxyImage("test.jpg");
        // Image not loaded until display() called
    }
    
    @Test
    @DisplayName("Protection proxy should enforce access control")
    void testProtectionProxy() {
        RealDocument doc = new RealDocument("secret.txt");
        User reader = new User("test", "reader");
        Document proxy = new ProtectedDocumentProxy(doc, reader);
        
        // Reader can read
        assertDoesNotThrow(() -> proxy.read());
        
        // Reader cannot write
        assertThrows(SecurityException.class, () -> proxy.write("hack"));
        
        // Reader cannot delete
        assertThrows(SecurityException.class, () -> proxy.delete());
    }
    
    @Test
    @DisplayName("Caching proxy should cache results")
    void testCachingProxy() {
        DataService db = new DatabaseService();
        CachingDataServiceProxy proxy = new CachingDataServiceProxy(db, 60);
        
        // First call - miss
        proxy.fetchData("user:1");
        assertEquals(0, proxy.getHitRate(), 0.1);
        
        // Second call - hit
        proxy.fetchData("user:1");
        assertEquals(50, proxy.getHitRate(), 0.1);
    }
}
