import java.util.ArrayDeque;
import java.util.Queue;

class Solution {
    public int coinChange(int[] coins, int amount) {
        if (amount == 0) {
            return 0;
        }
        boolean[] visited = new boolean[amount + 1];
        Queue<Integer> queue = new ArrayDeque<>();
        queue.add(0);
        visited[0] = true;
        int steps = 0;
        while (!queue.isEmpty()) {
            steps++;
            int size = queue.size();
            for (int i = 0; i < size; i++) {
                int current = queue.remove();
                for (int coin : coins) {
                    int next = current + coin;
                    if (next == amount) {
                        return steps;
                    }
                    if (next < amount && !visited[next]) {
                        visited[next] = true;
                        queue.add(next);
                    }
                }
            }
        }
        return -1;
    }
}
