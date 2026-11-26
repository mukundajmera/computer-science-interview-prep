import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;

public class InterviewSessionOrchestratorV1Test {
    @Test
    void startSessionInitialisesOrientationPhase() {
        InterviewSessionOrchestrator orchestrator = new InterviewSessionOrchestrator();
        InterviewSession session = orchestrator.startSession("s1", InterviewFormat.OPEN_ENDED);

        assertEquals("s1", session.getSessionId());
        assertEquals(InterviewFormat.OPEN_ENDED, session.getInterviewFormat());
        assertEquals(InterviewPhase.ORIENTATION, session.getCurrentPhase());
    }

    @Test
    void transitionAndEventLoggingWork() {
        InterviewSessionOrchestrator orchestrator = new InterviewSessionOrchestrator();
        InterviewSession session = orchestrator.startSession("s2", InterviewFormat.STRUCTURED);

        orchestrator.transitionPhase(session, InterviewPhase.IMPLEMENT);

        assertEquals(InterviewPhase.IMPLEMENT, session.getCurrentPhase());
        assertEquals(1, session.getEvents().size());
        assertEquals("phase_transition", session.getEvents().get(0).getEventType());
    }

    @Test
    void rubricObservationValidatesRange() {
        InterviewSessionOrchestrator orchestrator = new InterviewSessionOrchestrator();
        InterviewSession session = orchestrator.startSession("s3", InterviewFormat.STRUCTURED);

        assertThrows(
                IllegalArgumentException.class,
                () -> orchestrator.recordRubricObservation(session, RubricDimension.APPROACH, 0)
        );
    }
}
