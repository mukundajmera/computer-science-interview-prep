import java.util.ArrayList;
import java.util.List;
import java.util.Random;

class Solution {
    private final List<Integer> bag = new ArrayList<>();
    private final Random random = new Random(0);

    public Solution(int[] w) {
        for (int index = 0; index < w.length; index++) {
            for (int count = 0; count < w[index]; count++) {
                bag.add(index);
            }
        }
    }

    public int pickIndex() {
        return bag.get(random.nextInt(bag.size()));
    }
}
