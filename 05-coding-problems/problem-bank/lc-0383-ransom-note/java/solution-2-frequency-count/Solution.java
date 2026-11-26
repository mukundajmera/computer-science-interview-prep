import java.util.HashMap;
import java.util.Map;

class Solution {
    public boolean canConstruct(String ransomNote, String magazine) {
        Map<Character, Integer> counts = new HashMap<>();
        for (int i = 0; i < magazine.length(); i++) {
            char value = magazine.charAt(i);
            counts.put(value, counts.getOrDefault(value, 0) + 1);
        }
        for (int i = 0; i < ransomNote.length(); i++) {
            char value = ransomNote.charAt(i);
            int count = counts.getOrDefault(value, 0);
            if (count == 0) {
                return false;
            }
            counts.put(value, count - 1);
        }
        return true;
    }
}
