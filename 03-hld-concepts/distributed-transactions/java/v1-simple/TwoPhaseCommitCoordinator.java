package v1simple;

import java.util.ArrayList;
import java.util.List;
import java.util.Collections;

public class TwoPhaseCommitCoordinator {

    public interface Participant {
        boolean prepare();
        boolean commit();
        boolean abort();
    }

    private final List<Participant> participants;
    private final long timeoutMs;
    private final List<String> wal;

    public TwoPhaseCommitCoordinator(List<Participant> participants, long timeoutMs) {
        this.participants = participants;
        this.timeoutMs = timeoutMs;
        this.wal = new ArrayList<>();
    }

    public List<String> getWal() {
        return Collections.unmodifiableList(wal);
    }

    public boolean executeTransaction() {
        wal.add("TX_START");

        List<Participant> preparedParticipants = new ArrayList<>();
        boolean allPrepared = true;

        for (Participant p : participants) {
            try {
                // Mock timeout handling - in real world would use Future/Executors
                boolean vote = p.prepare();
                if (vote) {
                    preparedParticipants.add(p);
                    wal.add("PREPARE_OK");
                } else {
                    wal.add("PREPARE_NO");
                    allPrepared = false;
                    break;
                }
            } catch (Exception e) {
                wal.add("PREPARE_ERR");
                allPrepared = false;
                break;
            }
        }

        if (allPrepared) {
            wal.add("COMMIT_START");
            boolean commitSuccess = true;
            for (Participant p : preparedParticipants) {
                try {
                    boolean success = p.commit();
                    if (success) {
                        wal.add("COMMIT_OK");
                    } else {
                        wal.add("COMMIT_ERR");
                        commitSuccess = false;
                    }
                } catch (Exception e) {
                    wal.add("COMMIT_ERR");
                    commitSuccess = false;
                }
            }

            if (commitSuccess) {
                wal.add("TX_COMMITTED");
                return true;
            } else {
                wal.add("TX_INCONSISTENT"); // Requires manual intervention
                return false;
            }
        } else {
            wal.add("ABORT_START");
            for (Participant p : preparedParticipants) {
                try {
                    boolean success = p.abort();
                    if (success) {
                        wal.add("ABORT_OK");
                    } else {
                        wal.add("ABORT_ERR");
                    }
                } catch (Exception e) {
                    wal.add("ABORT_ERR");
                }
            }
            wal.add("TX_ABORTED");
            return false;
        }
    }

    public interface SagaStep {
        boolean execute();
        boolean compensate();
    }

    public static class SagaOrchestrator {
        private final List<SagaStep> steps;
        private String state;
        private final List<SagaStep> executedSteps;

        public SagaOrchestrator(List<SagaStep> steps) {
            this.steps = steps;
            this.state = "INIT";
            this.executedSteps = new ArrayList<>();
        }

        public String getState() {
            return state;
        }

        public boolean execute() {
            this.state = "RUNNING";

            for (SagaStep step : steps) {
                try {
                    boolean success = step.execute();
                    if (success) {
                        executedSteps.add(step);
                    } else {
                        this.state = "COMPENSATING";
                        compensate();
                        return false;
                    }
                } catch (Exception e) {
                    this.state = "COMPENSATING";
                    compensate();
                    return false;
                }
            }

            this.state = "COMPLETED";
            return true;
        }

        private void compensate() {
            for (int i = executedSteps.size() - 1; i >= 0; i--) {
                SagaStep step = executedSteps.get(i);
                try {
                    step.compensate();
                } catch (Exception e) {
                    // Log error, queue for manual intervention
                }
            }
            this.state = "COMPENSATED";
        }
    }
}
