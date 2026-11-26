import java.util.ArrayList;
import java.util.List;

class Solution {
    public int minimumTotal(List<List<Integer>> triangle) {
        List<Integer> costs = new ArrayList<>(triangle.get(triangle.size() - 1));

        for (int row = triangle.size() - 2; row >= 0; row--) {
            for (int col = 0; col <= row; col++) {
                int bestChild = Math.min(costs.get(col), costs.get(col + 1));
                costs.set(col, triangle.get(row).get(col) + bestChild);
            }
        }

        return costs.get(0);
    }
}
