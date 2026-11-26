import java.util.ArrayList;
import java.util.Collections;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;

class FileSystem {
    private final Map<String, Set<String>> directories = new HashMap<>();
    private final Map<String, StringBuilder> files = new HashMap<>();

    public FileSystem() {
        directories.put("/", new HashSet<>());
    }

    public List<String> ls(String path) {
        if (files.containsKey(path)) {
            int slash = path.lastIndexOf('/');
            return Collections.singletonList(path.substring(slash + 1));
        }
        List<String> result = new ArrayList<>(directories.getOrDefault(path, Collections.emptySet()));
        Collections.sort(result);
        return result;
    }

    public void mkdir(String path) {
        ensureDir(path);
    }

    public void addContentToFile(String filePath, String content) {
        int slash = filePath.lastIndexOf('/');
        String parent = slash == 0 ? "/" : filePath.substring(0, slash);
        ensureDir(parent);
        directories.get(parent).add(filePath.substring(slash + 1));
        files.computeIfAbsent(filePath, ignored -> new StringBuilder()).append(content);
    }

    public String readContentFromFile(String filePath) {
        return files.get(filePath).toString();
    }

    private void ensureDir(String path) {
        if (directories.containsKey(path)) {
            return;
        }
        String current = "";
        for (String part : path.split("/")) {
            if (part.isEmpty()) {
                current = "/";
                directories.putIfAbsent(current, new HashSet<>());
                continue;
            }
            String parent = current;
            current = current.equals("/") ? "/" + part : current + "/" + part;
            directories.putIfAbsent(current, new HashSet<>());
            directories.get(parent).add(part);
        }
    }
}
