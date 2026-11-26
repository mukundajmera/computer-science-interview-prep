class Solution {
    public int appendCharacters(String s, String t) {
        int start = 0;
        int matched = 0;
        for (int i = 0; i < t.length(); i++) {
            int found = s.indexOf(t.charAt(i), start);
            if (found < 0) {
                break;
            }
            matched++;
            start = found + 1;
        }
        return t.length() - matched;
    }
}
