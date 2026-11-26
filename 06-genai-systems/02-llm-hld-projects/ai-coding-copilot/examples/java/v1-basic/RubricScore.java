import java.util.EnumMap;
import java.util.Map;

public class RubricScore {
    private final Map<RubricDimension, Integer> scores = new EnumMap<>(RubricDimension.class);

    public void put(RubricDimension dimension, int score) {
        scores.put(dimension, score);
    }

    public Map<RubricDimension, Integer> getScores() {
        return scores;
    }
}
