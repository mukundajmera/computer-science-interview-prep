public class AICodingInterviewDemo {
    public static void main(String[] args) {
        InterviewSessionOrchestrator orchestrator = new InterviewSessionOrchestrator();
        InterviewSession session = orchestrator.startSession("demo-1", InterviewFormat.STRUCTURED);

        orchestrator.recordAiAction(session, "Prompted for interface-only skeleton");
        orchestrator.transitionPhase(session, InterviewPhase.IMPLEMENT);
        orchestrator.recordVerificationEvent(session, "Executed unit tests for modified module");
        orchestrator.transitionPhase(session, InterviewPhase.VERIFY);

        orchestrator.recordRubricObservation(session, RubricDimension.APPROACH, 4);
        orchestrator.recordRubricObservation(session, RubricDimension.CONTROL, 5);
        orchestrator.recordRubricObservation(session, RubricDimension.VERIFICATION, 4);
        orchestrator.recordRubricObservation(session, RubricDimension.COMMUNICATION, 4);

        System.out.println(orchestrator.sessionSummary(session));
    }
}
