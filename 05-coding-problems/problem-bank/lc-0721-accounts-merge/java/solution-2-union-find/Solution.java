import java.util.ArrayList;
import java.util.Collections;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

class Solution {
    public List<List<String>> accountsMerge(List<List<String>> accounts) {
        UnionFind uf = new UnionFind();
        Map<String, String> nameByEmail = new HashMap<>();
        for (List<String> account : accounts) {
            String name = account.get(0);
            String first = account.get(1);
            uf.add(first);
            for (int i = 1; i < account.size(); i++) {
                String email = account.get(i);
                nameByEmail.put(email, name);
                uf.add(email);
                uf.union(first, email);
            }
        }
        Map<String, List<String>> groups = new HashMap<>();
        for (String email : nameByEmail.keySet()) {
            groups.computeIfAbsent(uf.find(email), key -> new ArrayList<>()).add(email);
        }
        List<List<String>> result = new ArrayList<>();
        for (List<String> emails : groups.values()) {
            Collections.sort(emails);
            emails.add(0, nameByEmail.get(emails.get(0)));
            result.add(emails);
        }
        return result;
    }

    private static class UnionFind {
        private final Map<String, String> parent = new HashMap<>();

        private void add(String value) {
            parent.putIfAbsent(value, value);
        }

        private String find(String value) {
            String root = parent.get(value);
            if (!root.equals(value)) {
                root = find(root);
                parent.put(value, root);
            }
            return root;
        }

        private void union(String a, String b) {
            parent.put(find(a), find(b));
        }
    }
}
