import java.util.ArrayList;
import java.util.List;

class Solution {
    public int[] asteroidCollision(int[] asteroids) {
        List<Integer> current = new ArrayList<>();
        for (int asteroid : asteroids) {
            current.add(asteroid);
        }
        boolean changed = true;
        while (changed) {
            changed = false;
            List<Integer> next = new ArrayList<>();
            int index = 0;
            while (index < current.size()) {
                if (index + 1 < current.size() && current.get(index) > 0 && current.get(index + 1) < 0) {
                    changed = true;
                    int left = current.get(index);
                    int right = current.get(index + 1);
                    if (Math.abs(left) > Math.abs(right)) {
                        next.add(left);
                    } else if (Math.abs(left) < Math.abs(right)) {
                        next.add(right);
                    }
                    index += 2;
                } else {
                    next.add(current.get(index));
                    index++;
                }
            }
            current = next;
        }
        int[] result = new int[current.size()];
        for (int i = 0; i < current.size(); i++) {
            result[i] = current.get(i);
        }
        return result;
    }
}
