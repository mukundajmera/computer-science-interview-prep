import java.util.ArrayList;
import java.util.Collections;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

class FileSystem {
    private static class Node {
        Map<String, Node> children = new HashMap<>();
        StringBuilder content;
    }

    private final Node root = new Node();

    public List<String> ls(String path) {
        Node node = traverse(path, false);
        if (node.content != null) {
            int slash = path.lastIndexOf('/');
            return Collections.singletonList(path.substring(slash + 1));
        }
        List<String> result = new ArrayList<>(node.children.keySet());
        Collections.sort(result);
        return result;
    }

    public void mkdir(String path) {
        traverse(path, true);
    }

    public void addContentToFile(String filePath, String content) {
        Node node = traverse(filePath, true);
        if (node.content == null) {
            node.content = new StringBuilder();
        }
        node.content.append(content);
    }

    public String readContentFromFile(String filePath) {
        return traverse(filePath, false).content.toString();
    }

    private Node traverse(String path, boolean create) {
        Node node = root;
        for (String part : path.split("/")) {
            if (part.isEmpty()) {
                continue;
            }
            if (create) {
                node.children.putIfAbsent(part, new Node());
            }
            node = node.children.get(part);
        }
        return node;
    }
}
