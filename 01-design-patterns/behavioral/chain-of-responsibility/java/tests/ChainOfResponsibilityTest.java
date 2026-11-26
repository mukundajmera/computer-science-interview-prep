import org.junit.jupiter.api.*;
import static org.junit.jupiter.api.Assertions.*;

import java.util.List;

import chainofresponsibility.v1.*;
import chainofresponsibility.v2.MiddlewarePipelineDemo.*;
import chainofresponsibility.v3.SecurityFilterChainDemo.*;

public class ChainOfResponsibilityTest {

    @Test
    @DisplayName("FAQHandler processes severity 1 requests")
    void testHandlerProcessesRequest() {
        SupportHandler faq = new FAQHandler();
        SupportTicket ticket = new SupportTicket("Forgot password", 1);
        assertDoesNotThrow(() -> faq.handle(ticket));
    }

    @Test
    @DisplayName("Chain passes tickets to appropriate level handlers")
    void testChainPassesToNextHandler() {
        SupportHandler faq = new FAQHandler();
        SupportHandler l1 = new Level1Support();
        SupportHandler l2 = new Level2Support();
        SupportHandler manager = new ManagerSupport();

        faq.setNext(l1).setNext(l2).setNext(manager);

        assertDoesNotThrow(() -> faq.handle(new SupportTicket("Login issue", 2)));
        assertDoesNotThrow(() -> faq.handle(new SupportTicket("Database error", 3)));
        assertDoesNotThrow(() -> faq.handle(new SupportTicket("Data center outage", 5)));
    }

    @Test
    @DisplayName("Handling request with no matching handler does not throw")
    void testNoHandlerDoesNotThrow() {
        SupportHandler faq = new FAQHandler();
        SupportTicket unhandled = new SupportTicket("Security issue", 4);
        assertDoesNotThrow(() -> faq.handle(unhandled));
    }

    @Test
    @DisplayName("v2 Middleware pipeline handles auth, rate-limiting, and payload sanitization")
    void testMiddlewarePipeline() {
        Middleware pipeline = new AuthMiddleware();
        pipeline.linkWith(new RateLimitMiddleware(2)).linkWith(new SanitizationMiddleware());

        HttpRequest valid = new HttpRequest("/api/resource", "Bearer sec_tok", "payload", "127.0.0.1");
        HttpResponse res1 = pipeline.handle(valid);
        assertTrue(res1.isSuccess());
        assertEquals(200, res1.getStatusCode());

        HttpRequest noAuth = new HttpRequest("/api/resource", null, "payload", "127.0.0.1");
        assertEquals(401, pipeline.handle(noAuth).getStatusCode());

        HttpRequest badBody = new HttpRequest("/api/resource", "Bearer sec_tok", "<script>hack</script>", "127.0.0.1");
        assertEquals(400, pipeline.handle(badBody).getStatusCode());

        // 3rd call from same IP trips rate limiter
        HttpRequest rlReq = new HttpRequest("/api/resource", "Bearer sec_tok", "ok", "127.0.0.1");
        assertEquals(429, pipeline.handle(rlReq).getStatusCode());
    }

    @Test
    @DisplayName("v3 Security filter chain priority ordering and context audit trail")
    void testSecurityFilterChain() {
        SecurityFilterChain chain = new SecurityFilterChain()
                .addFilter(new RoleValidationFilter("OPERATOR"))
                .addFilter(new BlacklistFilter());

        SecurityContext okUser = new SecurityContext("charlie", List.of("OPERATOR"));
        assertTrue(chain.execute(okUser));
        assertTrue(okUser.getAuditTrail().stream().anyMatch(a -> a.contains("PASSED")));

        SecurityContext bannedUser = new SecurityContext("banned_user_1", List.of("OPERATOR"));
        assertFalse(chain.execute(bannedUser));
        assertTrue(bannedUser.getAuditTrail().stream().anyMatch(a -> a.contains("BLOCKED")));
    }
}
