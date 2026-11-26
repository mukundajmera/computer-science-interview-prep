import java.util.*;
class Solution {
    public List<TreeNode> generateTrees(int n) {
        if (n == 0) return new ArrayList<>();
        return build(1, n);
    }
    private List<TreeNode> build(int left, int right) {
        List<TreeNode> result = new ArrayList<>();
        if (left > right) {
            result.add(null);
            return result;
        }
        for (int rootValue = left; rootValue <= right; rootValue++) {
            for (TreeNode leftTree : build(left, rootValue - 1)) {
                for (TreeNode rightTree : build(rootValue + 1, right)) {
                    result.add(new TreeNode(rootValue, leftTree, rightTree));
                }
            }
        }
        return result;
    }
}
