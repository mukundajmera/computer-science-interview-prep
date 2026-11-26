import java.util.ArrayList;
import java.util.List;

class Solution {
    public List<List<String>> groupStrings(String[] strings) {
        boolean[] used = new boolean[strings.length];
        List<List<String>> groups = new ArrayList<>();
        for (int i = 0; i < strings.length; i++) {
            if (used[i]) continue;
            List<String> group = new ArrayList<>();
            for (int j = i; j < strings.length; j++) {
                if (!used[j] && same(strings[i], strings[j])) {
                    used[j] = true;
                    group.add(strings[j]);
                }
            }
            groups.add(group);
        }
        return groups;
    }
    private boolean same(String a, String b) {
        if (a.length() != b.length()) return false;
        if (a.isEmpty()) return true;
        int diff = (b.charAt(0) - a.charAt(0) + 26) % 26;
        for (int i = 1; i < a.length(); i++) if ((a.charAt(i) + diff - 'a') % 26 != b.charAt(i) - 'a') return false;
        return true;
    }
}
