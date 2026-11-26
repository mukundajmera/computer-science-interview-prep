import java.util.HashSet;
import java.util.Set;

public class CardinalityGuard {
    private final int maxSeries;
    private final Set<String> seenSeries = new HashSet<>();

    public CardinalityGuard(int maxSeries) {
        this.maxSeries = maxSeries;
    }

    public boolean accept(String seriesKey) {
        if (seenSeries.contains(seriesKey)) {
            return true;
        }
        if (seenSeries.size() >= maxSeries) {
            return false;
        }
        seenSeries.add(seriesKey);
        return true;
    }
}
