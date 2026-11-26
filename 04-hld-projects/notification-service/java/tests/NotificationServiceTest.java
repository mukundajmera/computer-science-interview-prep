import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

import java.util.Arrays;
import java.util.HashMap;
import java.util.Map;

class NotificationServiceTest {

    @Test
    void testTemplateRenderingSuccess() {
        NotificationTemplate template = new NotificationTemplate(
            "t1", 
            NotificationChannel.EMAIL, 
            "Welcome Email", 
            "Welcome {{name}}!", 
            "Hello {{name}}, your balance is {{balance}}.", 
            Arrays.asList("name", "balance")
        );
        
        Map<String, String> variables = new HashMap<>();
        variables.put("name", "Bob");
        variables.put("balance", "250");
        
        TemplateRenderer renderer = new TemplateRenderer();
        RenderedContent content = renderer.render(template, variables);
        
        assertEquals("Welcome Bob!", content.getSubject());
        assertEquals("Hello Bob, your balance is 250.", content.getBody());
    }

    @Test
    void testTemplateRenderingMissingVariable() {
        NotificationTemplate template = new NotificationTemplate(
            "t2", 
            NotificationChannel.SMS, 
            "Alert SMS", 
            null, 
            "Alert: {{issue}}", 
            Arrays.asList("issue")
        );
        
        Map<String, String> variables = new HashMap<>();
        TemplateRenderer renderer = new TemplateRenderer();
        
        IllegalArgumentException exception = assertThrows(IllegalArgumentException.class, () -> {
            renderer.render(template, variables);
        });
        
        assertTrue(exception.getMessage().contains("Missing required variable: issue"));
    }

    @Test
    void testChannelRouterFallback() {
        ChannelRouter router = new ChannelRouter();
        
        EmailProvider primaryEmail = new EmailProvider("PrimaryEmail");
        EmailProvider fallbackEmail = new EmailProvider("FallbackEmail");
        
        router.registerProvider(primaryEmail);
        router.registerProvider(fallbackEmail);
        
        // Both are healthy, should return primary
        ChannelProvider provider = router.getProvider(NotificationChannel.EMAIL);
        assertEquals(primaryEmail, provider);
        
        // Mark primary as unhealthy
        primaryEmail.setHealthy(false);
        
        // Should return fallback
        ChannelProvider provider2 = router.getProvider(NotificationChannel.EMAIL);
        assertEquals(fallbackEmail, provider2);
    }

    @Test
    void testChannelRouterMissingChannel() {
        ChannelRouter router = new ChannelRouter();
        
        IllegalStateException exception = assertThrows(IllegalStateException.class, () -> {
            router.getProvider(NotificationChannel.PUSH);
        });
        
        assertTrue(exception.getMessage().contains("No providers for channel"));
    }
}
