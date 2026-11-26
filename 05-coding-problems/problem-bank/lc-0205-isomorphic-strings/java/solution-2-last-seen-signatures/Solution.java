class Solution {
    public boolean isIsomorphic(String s, String t) {
        if (s.length() != t.length()) {
            return false;
        }
        int[] leftSeen = new int[Character.MAX_VALUE + 1];
        int[] rightSeen = new int[Character.MAX_VALUE + 1];
        for (int i = 0; i < s.length(); i++) {
            char left = s.charAt(i);
            char right = t.charAt(i);
            if (leftSeen[left] != rightSeen[right]) {
                return false;
            }
            leftSeen[left] = i + 1;
            rightSeen[right] = i + 1;
        }
        return true;
    }
}
