import java.util.HashSet;
import java.util.Set;

class Solution {
    public int lengthOfLongestSubstring(String s) {
        int best = 0;
        for (int start = 0; start < s.length(); start++) {
            Set<Character> seen = new HashSet<>();
            for (int end = start; end < s.length(); end++) {
                char ch = s.charAt(end);
                if (seen.contains(ch)) {
                    break;
                }
                seen.add(ch);
                best = Math.max(best, end - start + 1);
            }
        }
        return best;
    }
}
