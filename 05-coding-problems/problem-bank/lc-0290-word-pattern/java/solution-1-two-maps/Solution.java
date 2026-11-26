import java.util.HashMap;
import java.util.Map;

class Solution {
    public boolean wordPattern(String pattern, String s) {
        String[] words = s.split(" ");
        if (words.length != pattern.length()) {
            return false;
        }
        Map<Character, String> toWord = new HashMap<>();
        Map<String, Character> toChar = new HashMap<>();
        for (int i = 0; i < pattern.length(); i++) {
            char key = pattern.charAt(i);
            String word = words[i];
            if (toWord.containsKey(key) && !toWord.get(key).equals(word)) {
                return false;
            }
            if (toChar.containsKey(word) && toChar.get(word) != key) {
                return false;
            }
            toWord.put(key, word);
            toChar.put(word, key);
        }
        return true;
    }
}
