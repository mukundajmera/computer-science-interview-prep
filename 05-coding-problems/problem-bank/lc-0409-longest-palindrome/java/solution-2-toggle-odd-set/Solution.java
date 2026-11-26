import java.util.HashSet;
import java.util.Set;

class Solution {
    public int longestPalindrome(String s) {
        Set<Character> odd = new HashSet<>();
        int length = 0;
        for (int i = 0; i < s.length(); i++) {
            char ch = s.charAt(i);
            if (odd.remove(ch)) {
                length += 2;
            } else {
                odd.add(ch);
            }
        }
        return odd.isEmpty() ? length : length + 1;
    }
}
