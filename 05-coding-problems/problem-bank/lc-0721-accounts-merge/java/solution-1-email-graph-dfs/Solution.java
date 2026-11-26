import java.util.ArrayDeque;
import java.util.ArrayList;
import java.util.Collections;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;

class Solution {
    public List<List<String>> accountsMerge(List<List<String>> accounts) {
        Map<String, String> nameByEmail = new HashMap<>();
        Map<String, List<String>> graph = new HashMap<>();
        for (List<String> account : accounts) {
            String name = account.get(0);
            for (int i = 1; i < account.size(); i++) {
                String email = account.get(i);
                nameByEmail.put(email, name);
                graph.putIfAbsent(email, new ArrayList<>());
                if (i > 1) {
                    String prev = account.get(i - 1);
                    graph.get(email).add(prev);
                    graph.get(prev).add(email);
                }
            }
        }
        Set<String> seen = new HashSet<>();
        List<List<String>> result = new ArrayList<>();
        for (String email : graph.keySet()) {
            if (!seen.add(email)) {
                continue;
            }
            List<String> component = new ArrayList<>();
            ArrayDeque<String> stack = new ArrayDeque<>();
            stack.push(email);
            while (!stack.isEmpty()) {
                String current = stack.pop();
                component.add(current);
                for (String next : graph.get(current)) {
                    if (seen.add(next)) {
                        stack.push(next);
                    }
                }
            }
            Collections.sort(component);
            component.add(0, nameByEmail.get(email));
            result.add(component);
        }
        return result;
    }
}
