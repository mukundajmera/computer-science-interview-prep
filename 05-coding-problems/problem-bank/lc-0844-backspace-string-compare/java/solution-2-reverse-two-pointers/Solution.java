class Solution {
    public boolean backspaceCompare(String s, String t) {
        int left = s.length() - 1;
        int right = t.length() - 1;
        while (left >= 0 || right >= 0) {
            left = previousLiveIndex(s, left);
            right = previousLiveIndex(t, right);
            if (left < 0 || right < 0) {
                return left == right;
            }
            if (s.charAt(left) != t.charAt(right)) {
                return false;
            }
            left--;
            right--;
        }
        return true;
    }

    private int previousLiveIndex(String value, int index) {
        int skip = 0;
        while (index >= 0) {
            char current = value.charAt(index);
            if (current == '#') {
                skip++;
            } else if (skip > 0) {
                skip--;
            } else {
                return index;
            }
            index--;
        }
        return index;
    }
}
