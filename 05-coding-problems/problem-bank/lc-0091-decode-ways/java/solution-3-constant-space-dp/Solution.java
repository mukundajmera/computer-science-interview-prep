class Solution {
    public int numDecodings(String s) {
        int next = 1;
        int nextNext = 0;
        for (int index = s.length() - 1; index >= 0; index--) {
            int current = 0;
            if (s.charAt(index) != '0') {
                current = next;
                if (index + 1 < s.length()) {
                    int value = (s.charAt(index) - '0') * 10 + (s.charAt(index + 1) - '0');
                    if (value <= 26) {
                        current += nextNext;
                    }
                }
            }
            nextNext = next;
            next = current;
        }
        return next;
    }
}
