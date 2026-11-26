import java.util.Arrays;

class Solution {
    public int findCheapestPrice(int n, int[][] flights, int src, int dst, int k) {
        final int inf = 1_000_000_000;
        int[] previous = new int[n];
        Arrays.fill(previous, inf);
        previous[src] = 0;
        int answer = previous[dst];
        for (int edges = 1; edges <= k + 1; edges++) {
            int[] current = Arrays.copyOf(previous, n);
            for (int[] flight : flights) {
                if (previous[flight[0]] != inf) {
                    current[flight[1]] = Math.min(current[flight[1]], previous[flight[0]] + flight[2]);
                }
            }
            previous = current;
            answer = Math.min(answer, previous[dst]);
        }
        return answer == inf ? -1 : answer;
    }
}
