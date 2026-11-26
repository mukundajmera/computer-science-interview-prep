import java.util.ArrayList;
import java.util.List;

class Solution {
    public int[] asteroidCollision(int[] asteroids) {
        List<Integer> stack = new ArrayList<>();
        for (int asteroid : asteroids) {
            boolean alive = true;
            while (alive && asteroid < 0 && !stack.isEmpty() && stack.get(stack.size() - 1) > 0) {
                int top = stack.get(stack.size() - 1);
                if (top < -asteroid) {
                    stack.remove(stack.size() - 1);
                } else if (top == -asteroid) {
                    stack.remove(stack.size() - 1);
                    alive = false;
                } else {
                    alive = false;
                }
            }
            if (alive) {
                stack.add(asteroid);
            }
        }
        int[] result = new int[stack.size()];
        for (int i = 0; i < stack.size(); i++) {
            result[i] = stack.get(i);
        }
        return result;
    }
}
