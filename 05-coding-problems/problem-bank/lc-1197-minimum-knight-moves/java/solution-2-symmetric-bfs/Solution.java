import java.util.ArrayDeque;
import java.util.HashSet;
import java.util.Queue;
import java.util.Set;

class Solution {
    private static final int[][] MOVES = {{1, 2}, {2, 1}, {-1, 2}, {-2, 1}, {1, -2}, {2, -1}, {-1, -2}, {-2, -1}};

    public int minKnightMoves(int x, int y) {
        x = Math.abs(x);
        y = Math.abs(y);
        Queue<int[]> queue = new ArrayDeque<>();
        Set<String> seen = new HashSet<>();
        queue.add(new int[] {0, 0, 0});
        seen.add("0,0");
        while (!queue.isEmpty()) {
            int[] state = queue.remove();
            if (state[0] == x && state[1] == y) {
                return state[2];
            }
            for (int[] move : MOVES) {
                int nextX = state[0] + move[0];
                int nextY = state[1] + move[1];
                if (nextX < -2 || nextY < -2 || nextX > x + 2 || nextY > y + 2) {
                    continue;
                }
                String key = nextX + "," + nextY;
                if (seen.add(key)) {
                    queue.add(new int[] {nextX, nextY, state[2] + 1});
                }
            }
        }
        return -1;
    }
}
