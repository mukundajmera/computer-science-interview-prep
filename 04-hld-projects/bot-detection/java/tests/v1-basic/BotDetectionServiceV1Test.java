package v1;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

import java.time.Instant;
import java.util.Arrays;
import java.util.Collections;
import java.util.List;

import static org.junit.jupiter.api.Assertions.*;

public class BotDetectionServiceV1Test {

    private BotDetectionService service;

    @BeforeEach
    public void setUp() {
        service = new BotDetectionService();
    }

    @Test
    public void testEvaluateAccount_HighConfidenceBot_Suspends() {
        String accountId = "user123";
        // 6 signals of 0.95 -> high score, high confidence
        List<BotDetectionService.BehaviorSignal> signals = Arrays.asList(
            new BotDetectionService.BehaviorSignal(accountId, "LOGIN_RATE", 0.95, Instant.now()),
            new BotDetectionService.BehaviorSignal(accountId, "MSG_RATE", 0.95, Instant.now()),
            new BotDetectionService.BehaviorSignal(accountId, "FRIEND_REQ", 0.95, Instant.now()),
            new BotDetectionService.BehaviorSignal(accountId, "POST_RATE", 0.95, Instant.now()),
            new BotDetectionService.BehaviorSignal(accountId, "IP_REPUTATION", 0.95, Instant.now()),
            new BotDetectionService.BehaviorSignal(accountId, "USER_AGENT", 0.95, Instant.now())
        );

        BotDetectionService.ActionEvent action = service.evaluateAccount(accountId, signals);

        assertNotNull(action);
        assertEquals(BotDetectionService.AccountAction.SUSPEND, action.action);
        assertEquals("HIGH_CONFIDENCE_BOT", action.reasonCode);
        assertNotNull(action.rollbackRef);

        BotDetectionService.AccountRiskState status = service.getAccountStatus(accountId);
        assertEquals(BotDetectionService.AccountState.SUSPENDED, status.state);
        assertTrue(status.score > 0.9);
        assertTrue(status.confidence >= 0.8);
    }

    @Test
    public void testEvaluateAccount_MediumConfidenceHighScore_Limits() {
        String accountId = "user456";
        // 4 signals of 0.85 -> high score (>0.8), medium confidence (size > 2, size <= 5 -> 0.6)
        List<BotDetectionService.BehaviorSignal> signals = Arrays.asList(
            new BotDetectionService.BehaviorSignal(accountId, "LOGIN_RATE", 0.85, Instant.now()),
            new BotDetectionService.BehaviorSignal(accountId, "MSG_RATE", 0.85, Instant.now()),
            new BotDetectionService.BehaviorSignal(accountId, "FRIEND_REQ", 0.85, Instant.now()),
            new BotDetectionService.BehaviorSignal(accountId, "POST_RATE", 0.85, Instant.now())
        );

        BotDetectionService.ActionEvent action = service.evaluateAccount(accountId, signals);

        assertNotNull(action);
        assertEquals(BotDetectionService.AccountAction.LIMIT, action.action);

        BotDetectionService.AccountRiskState status = service.getAccountStatus(accountId);
        assertEquals(BotDetectionService.AccountState.LIMITED, status.state);
        assertEquals(0.6, status.confidence);
    }

    @Test
    public void testEvaluateAccount_LowConfidenceHighScore_RoutesToReview() {
        String accountId = "user789";
        // 2 signals of 0.9 -> high score, low confidence (size <= 2 -> 0.5)
        List<BotDetectionService.BehaviorSignal> signals = Arrays.asList(
            new BotDetectionService.BehaviorSignal(accountId, "LOGIN_RATE", 0.9, Instant.now()),
            new BotDetectionService.BehaviorSignal(accountId, "IP_REPUTATION", 0.9, Instant.now())
        );

        BotDetectionService.ActionEvent action = service.evaluateAccount(accountId, signals);

        assertNotNull(action);
        assertEquals(BotDetectionService.AccountAction.ROUTE_TO_REVIEW, action.action);

        BotDetectionService.AccountRiskState status = service.getAccountStatus(accountId);
        assertEquals(BotDetectionService.AccountState.UNDER_REVIEW, status.state);
        assertEquals(0.5, status.confidence);
    }

    @Test
    public void testEvaluateAccount_Suspicious_Challenges() {
         String accountId = "user_suspicious";
         // 1 signal of 0.65 -> score = 0.65, confidence = 0.5
         List<BotDetectionService.BehaviorSignal> signals = Collections.singletonList(
            new BotDetectionService.BehaviorSignal(accountId, "LOGIN_RATE", 0.65, Instant.now())
         );

         BotDetectionService.ActionEvent action = service.evaluateAccount(accountId, signals);

         assertNotNull(action);
         assertEquals(BotDetectionService.AccountAction.CHALLENGE, action.action);

         BotDetectionService.AccountRiskState status = service.getAccountStatus(accountId);
         assertEquals(BotDetectionService.AccountState.CHALLENGED, status.state);
    }

    @Test
    public void testEvaluateAccount_NormalActivity_NoAction() {
         String accountId = "user_normal";
         // signals of 0.1
         List<BotDetectionService.BehaviorSignal> signals = Arrays.asList(
            new BotDetectionService.BehaviorSignal(accountId, "LOGIN_RATE", 0.1, Instant.now()),
            new BotDetectionService.BehaviorSignal(accountId, "POST_RATE", 0.1, Instant.now())
         );

         BotDetectionService.ActionEvent action = service.evaluateAccount(accountId, signals);

         assertNull(action);

         BotDetectionService.AccountRiskState status = service.getAccountStatus(accountId);
         assertEquals(BotDetectionService.AccountState.ACTIVE, status.state);
         assertTrue(status.score < 0.5);
    }

    @Test
    public void testEvaluateAccount_InvalidInput() {
        assertThrows(IllegalArgumentException.class, () -> {
            service.evaluateAccount(null, Collections.emptyList());
        });
        assertThrows(IllegalArgumentException.class, () -> {
            service.evaluateAccount("", Collections.emptyList());
        });
    }

    @Test
    public void testAppealFlow() {
        String accountId = "user_appeal";
        // suspend
        List<BotDetectionService.BehaviorSignal> signals = Arrays.asList(
            new BotDetectionService.BehaviorSignal(accountId, "S1", 0.95, Instant.now()),
            new BotDetectionService.BehaviorSignal(accountId, "S2", 0.95, Instant.now()),
            new BotDetectionService.BehaviorSignal(accountId, "S3", 0.95, Instant.now()),
            new BotDetectionService.BehaviorSignal(accountId, "S4", 0.95, Instant.now()),
            new BotDetectionService.BehaviorSignal(accountId, "S5", 0.95, Instant.now()),
            new BotDetectionService.BehaviorSignal(accountId, "S6", 0.95, Instant.now())
        );
        service.evaluateAccount(accountId, signals);
        assertEquals(BotDetectionService.AccountState.SUSPENDED, service.getAccountStatus(accountId).state);

        // submit appeal
        service.submitAppeal(accountId, "I am not a bot!");

        // should be under review now
        assertEquals(BotDetectionService.AccountState.UNDER_REVIEW, service.getAccountStatus(accountId).state);
    }

    @Test
    public void testInvestigatorLabelFlow() {
        String accountId = "user_label";
        service.getAccountStatus(accountId); // initialize default active

        // investigator marks as bot
        service.submitInvestigatorLabel(accountId, "BOT", 0.9);

        BotDetectionService.AccountRiskState status = service.getAccountStatus(accountId);
        assertEquals(BotDetectionService.AccountState.SUSPENDED, status.state);
        assertEquals(1.0, status.confidence); // investigator 100% confidence

        // investigator marks as legitimate
        service.submitInvestigatorLabel(accountId, "LEGITIMATE", 1.0);
        status = service.getAccountStatus(accountId);
        assertEquals(BotDetectionService.AccountState.ACTIVE, status.state);
    }

    @Test
    public void testMetricsSnapshot() {
        String bot = "bot1";
        String susp = "susp1";

        List<BotDetectionService.BehaviorSignal> botSignals = Arrays.asList(
            new BotDetectionService.BehaviorSignal(bot, "S1", 0.95, Instant.now()),
            new BotDetectionService.BehaviorSignal(bot, "S2", 0.95, Instant.now()),
            new BotDetectionService.BehaviorSignal(bot, "S3", 0.95, Instant.now()),
            new BotDetectionService.BehaviorSignal(bot, "S4", 0.95, Instant.now()),
            new BotDetectionService.BehaviorSignal(bot, "S5", 0.95, Instant.now()),
            new BotDetectionService.BehaviorSignal(bot, "S6", 0.95, Instant.now())
        );
        service.evaluateAccount(bot, botSignals); // 1 suspension

        List<BotDetectionService.BehaviorSignal> suspSignals = Collections.singletonList(
            new BotDetectionService.BehaviorSignal(susp, "S1", 0.65, Instant.now())
        );
        service.evaluateAccount(susp, suspSignals); // 1 challenge

        BotDetectionService.MetricsSnapshot metrics = service.getMetricsSnapshot();
        assertEquals(2, metrics.totalAccountsEvaluated);
        assertEquals(1, metrics.totalSuspensions);
        assertEquals(1, metrics.totalChallenges);
        assertEquals(0, metrics.totalReviews);
    }
}
