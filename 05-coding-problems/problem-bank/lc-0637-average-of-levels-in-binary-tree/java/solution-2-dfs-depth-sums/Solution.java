import java.util.ArrayList;
import java.util.List;

class Solution {
    public List<Double> averageOfLevels(TreeNode root) {
        List<Double> sums = new ArrayList<>();
        List<Integer> counts = new ArrayList<>();
        collect(root, 0, sums, counts);

        List<Double> averages = new ArrayList<>();
        for (int depth = 0; depth < sums.size(); depth++) {
            averages.add(sums.get(depth) / counts.get(depth));
        }
        return averages;
    }

    private void collect(TreeNode node, int depth, List<Double> sums, List<Integer> counts) {
        if (node == null) {
            return;
        }
        if (depth == sums.size()) {
            sums.add(0.0);
            counts.add(0);
        }
        sums.set(depth, sums.get(depth) + node.val);
        counts.set(depth, counts.get(depth) + 1);
        collect(node.left, depth + 1, sums, counts);
        collect(node.right, depth + 1, sums, counts);
    }
}
