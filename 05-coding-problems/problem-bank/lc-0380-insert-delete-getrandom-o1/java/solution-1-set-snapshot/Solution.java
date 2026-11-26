import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Random;
import java.util.Set;

class RandomizedSet {
    private final Set<Integer> values = new HashSet<>();
    private final Random random = new Random();

    public boolean insert(int val) {
        return values.add(val);
    }

    public boolean remove(int val) {
        return values.remove(val);
    }

    public int getRandom() {
        List<Integer> snapshot = new ArrayList<>(values);
        return snapshot.get(random.nextInt(snapshot.size()));
    }
}
