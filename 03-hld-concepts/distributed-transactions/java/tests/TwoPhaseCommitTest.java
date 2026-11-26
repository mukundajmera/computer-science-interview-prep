package tests;

import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

import v1simple.TwoPhaseCommitCoordinator;
import v1simple.TwoPhaseCommitCoordinator.Participant;
import v1simple.TwoPhaseCommitCoordinator.SagaStep;
import v1simple.TwoPhaseCommitCoordinator.SagaOrchestrator;

import java.util.Arrays;

public class TwoPhaseCommitTest {

    static class MockParticipant implements Participant {
        boolean prepareRes = true;
        boolean commitRes = true;
        boolean abortRes = true;
        boolean throwOnPrepare = false;

        boolean prepared = false;
        boolean committed = false;
        boolean aborted = false;

        @Override
        public boolean prepare() {
            if (throwOnPrepare) throw new RuntimeException("Prepare error");
            if (prepareRes) {
                prepared = true;
                return true;
            }
            return false;
        }

        @Override
        public boolean commit() {
            if (commitRes) {
                committed = true;
                return true;
            }
            return false;
        }

        @Override
        public boolean abort() {
            if (abortRes) {
                aborted = true;
                return true;
            }
            return false;
        }
    }

    static class MockSagaStep implements SagaStep {
        boolean execRes = true;
        boolean compRes = true;
        boolean throwOnExec = false;

        boolean executed = false;
        boolean compensated = false;

        @Override
        public boolean execute() {
            if (throwOnExec) throw new RuntimeException("Execute error");
            if (execRes) {
                executed = true;
                return true;
            }
            return false;
        }

        @Override
        public boolean compensate() {
            if (compRes) {
                compensated = true;
                return true;
            }
            return false;
        }
    }

    @Test
    public void test2PCAllPrepareAndCommit() {
        MockParticipant p1 = new MockParticipant();
        MockParticipant p2 = new MockParticipant();

        TwoPhaseCommitCoordinator coordinator = new TwoPhaseCommitCoordinator(Arrays.asList(p1, p2), 1000);
        boolean result = coordinator.executeTransaction();

        assertTrue(result);
        assertTrue(p1.prepared && p1.committed && !p1.aborted);
        assertTrue(p2.prepared && p2.committed && !p2.aborted);
        assertTrue(coordinator.getWal().contains("TX_COMMITTED"));
    }

    @Test
    public void test2PCOnePrepareFailsCausesAbort() {
        MockParticipant p1 = new MockParticipant();
        MockParticipant p2 = new MockParticipant();
        p2.prepareRes = false;

        TwoPhaseCommitCoordinator coordinator = new TwoPhaseCommitCoordinator(Arrays.asList(p1, p2), 1000);
        boolean result = coordinator.executeTransaction();

        assertFalse(result);
        assertTrue(p1.prepared && !p1.committed && p1.aborted);
        assertFalse(p2.prepared || p2.committed || p2.aborted);
        assertTrue(coordinator.getWal().contains("TX_ABORTED"));
    }

    @Test
    public void testSagaAllStepsSucceed() {
        MockSagaStep s1 = new MockSagaStep();
        MockSagaStep s2 = new MockSagaStep();

        SagaOrchestrator orchestrator = new SagaOrchestrator(Arrays.asList(s1, s2));
        boolean result = orchestrator.execute();

        assertTrue(result);
        assertEquals("COMPLETED", orchestrator.getState());
        assertTrue(s1.executed && !s1.compensated);
        assertTrue(s2.executed && !s2.compensated);
    }

    @Test
    public void testSagaStepFailsCausesCompensation() {
        MockSagaStep s1 = new MockSagaStep();
        MockSagaStep s2 = new MockSagaStep();
        s2.execRes = false;

        SagaOrchestrator orchestrator = new SagaOrchestrator(Arrays.asList(s1, s2));
        boolean result = orchestrator.execute();

        assertFalse(result);
        assertEquals("COMPENSATED", orchestrator.getState());
        assertTrue(s1.executed && s1.compensated);
        assertTrue(!s2.executed && !s2.compensated);
    }
}
