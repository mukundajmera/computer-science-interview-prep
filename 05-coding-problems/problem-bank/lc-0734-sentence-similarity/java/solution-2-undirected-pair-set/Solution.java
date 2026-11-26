import java.util.HashSet;
import java.util.List;
import java.util.Set;

class Solution {
    public boolean areSentencesSimilar(String[] sentence1, String[] sentence2, List<List<String>> similarPairs) {
        if (sentence1.length != sentence2.length) {
            return false;
        }
        Set<String> pairs = new HashSet<>();
        for (List<String> pair : similarPairs) {
            pairs.add(pair.get(0) + "\u0000" + pair.get(1));
            pairs.add(pair.get(1) + "\u0000" + pair.get(0));
        }
        for (int i = 0; i < sentence1.length; i++) {
            if (!sentence1[i].equals(sentence2[i]) && !pairs.contains(sentence1[i] + "\u0000" + sentence2[i])) {
                return false;
            }
        }
        return true;
    }
}
