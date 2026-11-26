import java.util.HashMap;
import java.util.HashSet;
import java.util.Map;
import java.util.PriorityQueue;
import java.util.Set;

class Solution {
    public String alienOrder(String[] words) {
        Map<Character, Set<Character>> graph = new HashMap<>();
        Map<Character, Integer> indegree = new HashMap<>();
        for (String word : words) {
            for (char ch : word.toCharArray()) {
                graph.putIfAbsent(ch, new HashSet<>());
                indegree.putIfAbsent(ch, 0);
            }
        }
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
                    return "";
                }
            } else if (graph.get(first.charAt(index)).add(second.charAt(index))) {
                indegree.put(second.charAt(index), indegree.get(second.charAt(index)) + 1);
            }
        }
        PriorityQueue<Character> heap = new PriorityQueue<>();
        for (Map.Entry<Character, Integer> entry : indegree.entrySet()) {
            if (entry.getValue() == 0) {
                heap.add(entry.getKey());
            }
        }
        StringBuilder order = new StringBuilder();
        while (!heap.isEmpty()) {
            char ch = heap.remove();
            order.append(ch);
            for (char next : graph.get(ch)) {
                indegree.put(next, indegree.get(next) - 1);
                if (indegree.get(next) == 0) {
                    heap.add(next);
                }
            }
        }
        return order.length() == indegree.size() ? order.toString() : "";
    }
}
