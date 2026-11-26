import java.util.ArrayList;
import java.util.List;

class Solution {
    public boolean validWordSquare(List<String> words) {
        int max = 0;
        for (String word : words) {
            max = Math.max(max, word.length());
        }
        if (max != words.size()) {
            return false;
        }
        for (int col = 0; col < words.size(); col++) {
            StringBuilder builder = new StringBuilder();
            for (String word : words) {
                if (col < word.length()) {
                    builder.append(word.charAt(col));
                }
            }
            if (!builder.toString().equals(words.get(col))) {
                return false;
            }
        }
        return true;
    }
}
