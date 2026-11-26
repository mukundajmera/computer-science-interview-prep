import java.util.ArrayList;
import java.util.List;

class BSTIterator {
    private final List<Integer> values = new ArrayList<>();
    private int index = 0;

    public BSTIterator(TreeNode root) {
        inorder(root);
    }

    public int next() {
        int value = values.get(index);
        index += 1;
        return value;
    }

    public boolean hasNext() {
        return index < values.size();
    }

    private void inorder(TreeNode node) {
        if (node == null) {
            return;
        }
        inorder(node.left);
        values.add(node.val);
        inorder(node.right);
    }
}
