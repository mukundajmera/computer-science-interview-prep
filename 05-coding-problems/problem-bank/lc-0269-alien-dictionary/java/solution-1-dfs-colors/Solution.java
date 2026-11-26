import java.util.ArrayList;
import java.util.Collections;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;

class Solution {
    public String alienOrder(String[] words) {
        Map<Character, Set<Character>> graph = new HashMap<>();
        for (String word : words) {
            for (char ch : word.toCharArray()) {
                graph.putIfAbsent(ch, new HashSet<>());
            }
        }
        if (!buildEdges(words, graph)) {
            return "";
        }
        Map<Character, Integer> color = new HashMap<>();
        StringBuilder order = new StringBuilder();
        List<Character> chars = new ArrayList<>(graph.keySet());
        Collections.sort(chars);
        for (char ch : chars) {
            if (color.getOrDefault(ch, 0) == 0 && hasCycle(ch, graph, color, order)) {
                return "";
            }
        }
        return order.reverse().toString();
    }

    private boolean buildEdges(String[] words, Map<Character, Set<Character>> graph) {
        for (int i = 0; i + 1 < words.length; i++) {
            String first = words[i];
            String second = words[i + 1];
            int limit = Math.min(first.length(), second.length());
            int index = 0;
            while (index < limit && first.charAt(index) == second.charAt(index)) {
                index++;
            }
            if (index == limit) {
                if (first.length() > second.length()) {
                    return false;
                }
            } else {
                graph.get(first.charAt(index)).add(second.charAt(index));
            }
        }
        return true;
    }

    private boolean hasCycle(char ch, Map<Character, Set<Character>> graph, Map<Character, Integer> color, StringBuilder order) {
        color.put(ch, 1);
        List<Character> neighbors = new ArrayList<>(graph.get(ch));
        Collections.sort(neighbors);
        for (char next : neighbors) {
            int state = color.getOrDefault(next, 0);
            if (state == 1 || (state == 0 && hasCycle(next, graph, color, order))) {
                return true;
            }
        }
        color.put(ch, 2);
        order.append(ch);
        return false;
    }
}
