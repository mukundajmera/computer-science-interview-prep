import java.util.ArrayList;
import java.util.List;

public class PatternEvaluator {

    public List<String> evaluate(SystemRequirements req) {
        List<String> patterns = new ArrayList<>();

        // High read ratio with acceptable eventual consistency or strict latency
        if (req.getReadWriteRatio() > 5.0 && req.getLatencySlaMs() < 50) {
            patterns.add("Cache-Aside");
        }

        // Heavy writes
        if (req.getReadWriteRatio() < 0.5 && req.getThroughputTps() > 10000) {
            if (req.getConsistencyLevel() == ConsistencyLevel.EVENTUAL) {
                patterns.add("Write-Behind");
            } else {
                patterns.add("Event Sourcing");
            }
        }

        // High throughput, low latency, heavy writes -> Async processing
        if (req.getThroughputTps() > 10000 && req.getLatencySlaMs() > 100) {
            patterns.add("Message Queue / Worker Pool");
        }

        // Very high throughput, eventual consistency
        if (req.getThroughputTps() > 50000 && req.getConsistencyLevel() == ConsistencyLevel.EVENTUAL) {
            patterns.add("CQRS");
        }

        // Strict consistency required with distributed system characteristics
        if (req.getConsistencyLevel() == ConsistencyLevel.STRONG && req.getThroughputTps() < 5000) {
            patterns.add("2PC (Two-Phase Commit)");
        }

        // Read heavy, very low latency
        if (req.getReadWriteRatio() > 100 && req.getLatencySlaMs() < 20) {
            patterns.add("CDN");
        }

        if (patterns.isEmpty()) {
            patterns.add("Standard 3-Tier Architecture");
        }

        return patterns;
    }
}
