import java.util.ArrayList;
import java.util.List;

class Solution {
    public int scoreOfString(String s) {
        List<Integer> diffs = new ArrayList<>();
        for (int i = 1; i < s.length(); i++) {
            diffs.add(Math.abs(s.charAt(i) - s.charAt(i - 1)));
        }
        int total = 0;
        for (int diff : diffs) {
            total += diff;
        }
        return total;
    }
}
