import java.util.HashMap;
import java.util.Map;

public class InterviewSessionOrchestrator {
    public InterviewSession startSession(String sessionId, InterviewFormat interviewFormat) {
        return new InterviewSession(sessionId, interviewFormat);
    }

    public void transitionPhase(InterviewSession session, InterviewPhase nextPhase) {
        session.setCurrentPhase(nextPhase);
        session.getEvents().add(new SessionEvent("phase_transition", nextPhase.name()));
    }

    public void recordAiAction(InterviewSession session, String promptSummary) {
        session.getEvents().add(new SessionEvent("ai_action", promptSummary));
    }

    public void recordVerificationEvent(InterviewSession session, String verificationSummary) {
        session.getEvents().add(new SessionEvent("verification_event", verificationSummary));
    }

    public void recordRubricObservation(InterviewSession session, RubricDimension dimension, int score) {
        if (score < 1 || score > 5) {
            throw new IllegalArgumentException("score must be between 1 and 5");
        }
        session.getRubricScore().put(dimension, score);
    }

    public Map<String, Object> sessionSummary(InterviewSession session) {
        Map<RubricDimension, Integer> scores = session.getRubricScore().getScores();
        double average = 0.0;
        if (!scores.isEmpty()) {
            int total = 0;
            for (Integer value : scores.values()) {
                total += value;
            }
            average = (double) total / scores.size();
        }

        Map<String, Object> summary = new HashMap<>();
        summary.put("sessionId", session.getSessionId());
        summary.put("format", session.getInterviewFormat().name());
        summary.put("phase", session.getCurrentPhase().name());
        summary.put("events", session.getEvents().size());
        summary.put("rubricAverage", Math.round(average * 100.0) / 100.0);
        return summary;
    }
}
