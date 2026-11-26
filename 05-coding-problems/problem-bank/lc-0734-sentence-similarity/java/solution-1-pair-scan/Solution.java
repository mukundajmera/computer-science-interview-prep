import java.util.List;

class Solution {
    public boolean areSentencesSimilar(String[] sentence1, String[] sentence2, List<List<String>> similarPairs) {
        if (sentence1.length != sentence2.length) {
            return false;
        }
        for (int i = 0; i < sentence1.length; i++) {
            if (sentence1[i].equals(sentence2[i])) {
                continue;
            }
            boolean matched = false;
            for (List<String> pair : similarPairs) {
                if ((pair.get(0).equals(sentence1[i]) && pair.get(1).equals(sentence2[i])) || (pair.get(1).equals(sentence1[i]) && pair.get(0).equals(sentence2[i]))) {
                    matched = true;
                    break;
                }
            }
            if (!matched) {
                return false;
            }
        }
        return true;
    }
}
