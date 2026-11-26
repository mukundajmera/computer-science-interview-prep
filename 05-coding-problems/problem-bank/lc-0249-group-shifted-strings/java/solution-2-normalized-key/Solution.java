import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

class Solution {
    public List<List<String>> groupStrings(String[] strings) {
        Map<String, List<String>> groups = new HashMap<>();
        for (String value : strings) groups.computeIfAbsent(key(value), ignored -> new ArrayList<>()).add(value);
        return new ArrayList<>(groups.values());
    }
    private String key(String value) {
        StringBuilder builder = new StringBuilder();
        int base = value.charAt(0) - 'a';
        for (int i = 0; i < value.length(); i++) builder.append((value.charAt(i) - 'a' - base + 26) % 26).append('#');
        return builder.toString();
    }
}
