class Solution {
    public int findMaximizedCapital(int k, int w, int[] profits, int[] capital) {
        boolean[] used = new boolean[profits.length];
        int current = w;
        for (int round = 0; round < k; round++) {
            int bestIndex = -1;
            int bestProfit = -1;
            for (int i = 0; i < profits.length; i++) {
                if (!used[i] && capital[i] <= current && profits[i] > bestProfit) {
                    bestProfit = profits[i];
                    bestIndex = i;
                }
            }
            if (bestIndex == -1) {
                break;
            }
            used[bestIndex] = true;
            current += profits[bestIndex];
        }
        return current;
    }
}
