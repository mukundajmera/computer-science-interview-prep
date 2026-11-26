package v1;

import java.util.*;
import java.time.Instant;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.CopyOnWriteArrayList;
import java.util.stream.Collectors;

public class BotDetectionService {

    public enum AccountState {
        ACTIVE, LIMITED, CHALLENGED, DEMOTED, SUSPENDED, UNDER_REVIEW
    }

    public enum AccountAction {
        LIMIT, CHALLENGE, DEMOTE, SUSPEND, ROUTE_TO_REVIEW, NONE
    }

    public static class AccountRiskState {
        public final String accountId;
        public final double score;
        public final double confidence;
        public final AccountState state;
        public final String policyVersion;
        public final String modelVersion;
        public final Instant updatedAt;

        public AccountRiskState(String accountId, double score, double confidence, AccountState state, String policyVersion, String modelVersion, Instant updatedAt) {
            this.accountId = accountId;
            this.score = score;
            this.confidence = confidence;
            this.state = state;
            this.policyVersion = policyVersion;
            this.modelVersion = modelVersion;
            this.updatedAt = updatedAt;
        }
    }

    public static class BehaviorSignal {
        public final String accountId;
        public final String signalType;
        public final double signalValue;
        public final Instant eventTime;

        public BehaviorSignal(String accountId, String signalType, double signalValue, Instant eventTime) {
            this.accountId = accountId;
            this.signalType = signalType;
            this.signalValue = signalValue;
            this.eventTime = eventTime;
        }
    }

    public static class ActionEvent {
        public final String accountId;
        public final AccountAction action;
        public final String reasonCode;
        public final Instant issuedAt;
        public final String policyVersion;
        public final String modelVersion;
        public final String rollbackRef;

        public ActionEvent(String accountId, AccountAction action, String reasonCode, Instant issuedAt, String policyVersion, String modelVersion, String rollbackRef) {
            this.accountId = accountId;
            this.action = action;
            this.reasonCode = reasonCode;
            this.issuedAt = issuedAt;
            this.policyVersion = policyVersion;
            this.modelVersion = modelVersion;
            this.rollbackRef = rollbackRef;
        }
    }

    public static class InvestigatorLabel {
        public final String accountId;
        public final String label;
        public final double quality;
        public final Instant createdAt;

        public InvestigatorLabel(String accountId, String label, double quality, Instant createdAt) {
            this.accountId = accountId;
            this.label = label;
            this.quality = quality;
            this.createdAt = createdAt;
        }
    }

    public static class Appeal {
        public final String accountId;
        public final String reason;
        public final Instant submittedAt;

        public Appeal(String accountId, String reason, Instant submittedAt) {
            this.accountId = accountId;
            this.reason = reason;
            this.submittedAt = submittedAt;
        }
    }

    public static class MetricsSnapshot {
        public final int totalAccountsEvaluated;
        public final int totalSuspensions;
        public final int totalChallenges;
        public final int totalReviews;

        public MetricsSnapshot(int totalAccountsEvaluated, int totalSuspensions, int totalChallenges, int totalReviews) {
            this.totalAccountsEvaluated = totalAccountsEvaluated;
            this.totalSuspensions = totalSuspensions;
            this.totalChallenges = totalChallenges;
            this.totalReviews = totalReviews;
        }
    }

    private final Map<String, AccountRiskState> accountStates = new ConcurrentHashMap<>();
    private final List<ActionEvent> actionEvents = new CopyOnWriteArrayList<>();
    private final List<InvestigatorLabel> investigatorLabels = new CopyOnWriteArrayList<>();
    private final List<Appeal> appeals = new CopyOnWriteArrayList<>();

    private final String currentPolicyVersion = "1.0.0";
    private final String currentModelVersion = "1.0.0";

    public ActionEvent evaluateAccount(String accountId, List<BehaviorSignal> signals) {
        if (accountId == null || accountId.isEmpty()) {
            throw new IllegalArgumentException("Account ID cannot be null or empty");
        }

        // 1. Compute Score and Confidence
        double score = 0.0;
        double confidence = 0.5; // default

        if (signals != null && !signals.isEmpty()) {
            double totalValue = 0.0;
            int anomalousSignals = 0;
            for (BehaviorSignal s : signals) {
                totalValue += s.signalValue;
                if (s.signalValue > 0.8) {
                    anomalousSignals++;
                }
            }
            score = totalValue / signals.size();

            // Adjust confidence based on number of anomalous signals
            if (signals.size() > 5) {
                confidence = 0.8;
            } else if (signals.size() > 2) {
                confidence = 0.6;
            }

            if (anomalousSignals > 3) {
                score = Math.min(1.0, score + 0.2); // boost score
            }
        }

        // 2. Policy Engine: Map to Action
        AccountAction actionToTake = AccountAction.NONE;
        AccountState newState = AccountState.ACTIVE;
        String reasonCode = "OK";

        if (score >= 0.9 && confidence >= 0.8) {
            actionToTake = AccountAction.SUSPEND;
            newState = AccountState.SUSPENDED;
            reasonCode = "HIGH_CONFIDENCE_BOT";
        } else if (score >= 0.8) {
             // High score, lower confidence -> Route to review or limit
             if (confidence < 0.6) {
                 actionToTake = AccountAction.ROUTE_TO_REVIEW;
                 newState = AccountState.UNDER_REVIEW;
                 reasonCode = "UNCERTAIN_HIGH_SCORE";
             } else {
                 actionToTake = AccountAction.LIMIT;
                 newState = AccountState.LIMITED;
                 reasonCode = "MED_CONFIDENCE_HIGH_SCORE";
             }
        } else if (score >= 0.6) {
             actionToTake = AccountAction.CHALLENGE;
             newState = AccountState.CHALLENGED;
             reasonCode = "SUSPICIOUS_ACTIVITY";
        }

        // 3. Record Action and State
        AccountRiskState state = new AccountRiskState(
            accountId, score, confidence, newState,
            currentPolicyVersion, currentModelVersion, Instant.now()
        );
        accountStates.put(accountId, state);

        if (actionToTake != AccountAction.NONE) {
            String rollbackRef = UUID.randomUUID().toString();
            ActionEvent actionEvent = new ActionEvent(
                accountId, actionToTake, reasonCode, Instant.now(),
                currentPolicyVersion, currentModelVersion, rollbackRef
            );
            actionEvents.add(actionEvent);
            return actionEvent;
        }

        return null; // No action taken
    }

    public AccountRiskState getAccountStatus(String accountId) {
        return accountStates.getOrDefault(accountId,
            new AccountRiskState(accountId, 0.0, 0.0, AccountState.ACTIVE, currentPolicyVersion, currentModelVersion, Instant.now()));
    }

    public void submitAppeal(String accountId, String reason) {
        if (accountId == null || reason == null) {
            throw new IllegalArgumentException("Invalid appeal data");
        }
        appeals.add(new Appeal(accountId, reason, Instant.now()));

        // If they appeal, put them in review state if they are suspended or limited
        AccountRiskState currentState = getAccountStatus(accountId);
        if (currentState.state == AccountState.SUSPENDED || currentState.state == AccountState.LIMITED || currentState.state == AccountState.CHALLENGED) {
             accountStates.put(accountId, new AccountRiskState(
                accountId, currentState.score, currentState.confidence, AccountState.UNDER_REVIEW,
                currentState.policyVersion, currentState.modelVersion, Instant.now()
             ));
        }
    }

    public void submitInvestigatorLabel(String accountId, String label, double quality) {
        if (accountId == null || label == null) {
             throw new IllegalArgumentException("Invalid label data");
        }
        investigatorLabels.add(new InvestigatorLabel(accountId, label, quality, Instant.now()));

        // Investigator label can override state
        AccountState newState = AccountState.ACTIVE;
        if ("BOT".equalsIgnoreCase(label)) {
            newState = AccountState.SUSPENDED;
        } else if ("LEGITIMATE".equalsIgnoreCase(label)) {
            newState = AccountState.ACTIVE;
        } else if ("SPAMMER".equalsIgnoreCase(label)) {
            newState = AccountState.DEMOTED;
        }

        AccountRiskState currentState = getAccountStatus(accountId);
        accountStates.put(accountId, new AccountRiskState(
            accountId, currentState.score, 1.0, newState, // 100% confidence from investigator
            currentState.policyVersion, currentState.modelVersion, Instant.now()
        ));
    }

    public MetricsSnapshot getMetricsSnapshot() {
        int totalAccounts = accountStates.size();
        int totalSuspensions = 0;
        int totalChallenges = 0;
        int totalReviews = 0;

        for (ActionEvent event : actionEvents) {
            if (event.action == AccountAction.SUSPEND) totalSuspensions++;
            else if (event.action == AccountAction.CHALLENGE) totalChallenges++;
            else if (event.action == AccountAction.ROUTE_TO_REVIEW) totalReviews++;
        }

        return new MetricsSnapshot(totalAccounts, totalSuspensions, totalChallenges, totalReviews);
    }
}
