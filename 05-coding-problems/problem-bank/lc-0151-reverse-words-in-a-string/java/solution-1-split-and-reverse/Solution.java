import java.util.ArrayList;
import java.util.Collections;
import java.util.List;

class Solution {
    public String reverseWords(String s) {
        String[] raw = s.trim().split("\\s+");
        List<String> words = new ArrayList<>();
        for (String word : raw) {
            if (!word.isEmpty()) {
                words.add(word);
            }
        }
        Collections.reverse(words);
        return String.join(" ", words);
    }
}
