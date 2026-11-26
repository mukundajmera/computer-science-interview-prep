import java.util.ArrayList;
import java.util.List;

public class InterviewSession {
    private final String sessionId;
    private final InterviewFormat interviewFormat;
    private InterviewPhase currentPhase;
    private final List<SessionEvent> events;
    private final RubricScore rubricScore;

    public InterviewSession(String sessionId, InterviewFormat interviewFormat) {
        this.sessionId = sessionId;
        this.interviewFormat = interviewFormat;
        this.currentPhase = InterviewPhase.ORIENTATION;
        this.events = new ArrayList<>();
        this.rubricScore = new RubricScore();
    }

    public String getSessionId() {
        return sessionId;
    }

    public InterviewFormat getInterviewFormat() {
        return interviewFormat;
    }

    public InterviewPhase getCurrentPhase() {
        return currentPhase;
    }

    public void setCurrentPhase(InterviewPhase currentPhase) {
        this.currentPhase = currentPhase;
    }

    public List<SessionEvent> getEvents() {
        return events;
    }

    public RubricScore getRubricScore() {
        return rubricScore;
    }
}
