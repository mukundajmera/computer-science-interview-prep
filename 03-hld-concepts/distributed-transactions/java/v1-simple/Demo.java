package v1simple;

import java.util.Arrays;
import java.util.List;

public class Demo {
    public static void main(String[] args) {
        System.out.println("--- 2PC Demo ---");

        TwoPhaseCommitCoordinator.Participant p1 = new MockParticipant("DB1");
        TwoPhaseCommitCoordinator.Participant p2 = new MockParticipant("DB2");

        TwoPhaseCommitCoordinator coordinator = new TwoPhaseCommitCoordinator(Arrays.asList(p1, p2), 1000);
        boolean success = coordinator.executeTransaction();
        System.out.println("2PC transaction success: " + success);
        System.out.println("WAL: " + coordinator.getWal());


        System.out.println("\n--- Saga Demo ---");

        TwoPhaseCommitCoordinator.SagaStep s1 = new MockSagaStep("Reserve Inventory", true);
        TwoPhaseCommitCoordinator.SagaStep s2 = new MockSagaStep("Charge Payment", false); // Will fail

        TwoPhaseCommitCoordinator.SagaOrchestrator orchestrator = new TwoPhaseCommitCoordinator.SagaOrchestrator(Arrays.asList(s1, s2));
        boolean sagaSuccess = orchestrator.execute();
        System.out.println("Saga success: " + sagaSuccess);
        System.out.println("Saga final state: " + orchestrator.getState());
    }

    static class MockParticipant implements TwoPhaseCommitCoordinator.Participant {
        private final String name;

        public MockParticipant(String name) {
            this.name = name;
        }

        @Override
        public boolean prepare() {
            System.out.println(name + " preparing...");
            return true;
        }

        @Override
        public boolean commit() {
            System.out.println(name + " committing...");
            return true;
        }

        @Override
        public boolean abort() {
            System.out.println(name + " aborting...");
            return true;
        }
    }

    static class MockSagaStep implements TwoPhaseCommitCoordinator.SagaStep {
        private final String name;
        private final boolean success;

        public MockSagaStep(String name, boolean success) {
            this.name = name;
            this.success = success;
        }

        @Override
        public boolean execute() {
            System.out.println(name + " executing...");
            return success;
        }

        @Override
        public boolean compensate() {
            System.out.println(name + " compensating...");
            return true;
        }
    }
}
