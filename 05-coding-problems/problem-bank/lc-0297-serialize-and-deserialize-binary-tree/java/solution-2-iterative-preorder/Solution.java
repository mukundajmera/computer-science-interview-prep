import java.util.ArrayList;
import java.util.List;

class Codec {
    public String serialize(TreeNode root) {
        StringBuilder builder = new StringBuilder();
        List<TreeNode> stack = new ArrayList<>();
        stack.add(root);
        while (!stack.isEmpty()) {
            TreeNode node = stack.remove(stack.size() - 1);
            if (node == null) {
                builder.append("#,");
                continue;
            }
            builder.append(node.val).append(',');
            stack.add(node.right);
            stack.add(node.left);
        }
        builder.setLength(builder.length() - 1);
        return builder.toString();
    }

    public TreeNode deserialize(String data) {
        String[] tokens = data.split(",", -1);
        int[] index = {0};
        return build(tokens, index);
    }

    private TreeNode build(String[] tokens, int[] index) {
        String token = tokens[index[0]++];
        if (token.equals("#")) {
            return null;
        }
        TreeNode node = new TreeNode(Integer.parseInt(token));
        node.left = build(tokens, index);
        node.right = build(tokens, index);
        return node;
    }
}
