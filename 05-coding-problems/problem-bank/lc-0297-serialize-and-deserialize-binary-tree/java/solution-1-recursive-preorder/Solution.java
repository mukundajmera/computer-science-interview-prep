import java.util.ArrayDeque;
import java.util.Arrays;
import java.util.Queue;

class Codec {
    public String serialize(TreeNode root) {
        StringBuilder builder = new StringBuilder();
        serialize(root, builder);
        if (builder.length() > 0 && builder.charAt(builder.length() - 1) == ',') {
            builder.setLength(builder.length() - 1);
        }
        return builder.toString();
    }

    private void serialize(TreeNode node, StringBuilder builder) {
        if (node == null) {
            builder.append("#,");
            return;
        }
        builder.append(node.val).append(',');
        serialize(node.left, builder);
        serialize(node.right, builder);
    }

    public TreeNode deserialize(String data) {
        Queue<String> tokens = new ArrayDeque<>(Arrays.asList(data.split(",", -1)));
        return build(tokens);
    }

    private TreeNode build(Queue<String> tokens) {
        String token = tokens.remove();
        if (token.equals("#")) {
            return null;
        }
        TreeNode node = new TreeNode(Integer.parseInt(token));
        node.left = build(tokens);
        node.right = build(tokens);
        return node;
    }
}
