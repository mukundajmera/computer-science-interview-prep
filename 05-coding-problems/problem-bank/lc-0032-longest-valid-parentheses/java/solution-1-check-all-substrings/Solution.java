class Solution {
    public int longestValidParentheses(String s) {
        int best = 0;
        for (int start = 0; start < s.length(); start++) {
            for (int end = start + 2; end <= s.length(); end += 2) {
                if (end - start > best && isValid(s, start, end)) {
                    best = end - start;
                }
            }
        }
        return best;
    }

    private boolean isValid(String s, int start, int end) {
        int balance = 0;
        for (int index = start; index < end; index++) {
            balance += s.charAt(index) == '(' ? 1 : -1;
            if (balance < 0) {
                return false;
            }
        }
        return balance == 0;
    }
}
