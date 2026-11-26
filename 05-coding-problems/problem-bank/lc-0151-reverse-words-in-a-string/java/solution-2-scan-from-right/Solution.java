import java.util.ArrayList;
import java.util.List;

class Solution {
    public String reverseWords(String s) {
        List<String> words = new ArrayList<>();
        int i = s.length() - 1;
        while (i >= 0) {
            while (i >= 0 && s.charAt(i) == ' ') {
                i--;
            }
            int end = i;
            while (i >= 0 && s.charAt(i) != ' ') {
                i--;
            }
            if (end >= 0) {
                words.add(s.substring(i + 1, end + 1));
            }
        }
        return String.join(" ", words);
    }
}
