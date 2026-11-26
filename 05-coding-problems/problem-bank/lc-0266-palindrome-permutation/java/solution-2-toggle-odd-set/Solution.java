import java.util.HashSet;
import java.util.Set;

class Solution {
    public boolean canPermutePalindrome(String s) {
        Set<Character> odd = new HashSet<>();
        for (char c : s.toCharArray()) {
            if (!odd.add(c)) odd.remove(c);
        }
        return odd.size() <= 1;
    }
}
