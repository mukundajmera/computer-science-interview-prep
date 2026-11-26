class Solution {
    public int longestValidParentheses(String s) {
        return Math.max(scan(s, 0, s.length(), 1), scan(s, s.length() - 1, -1, -1));
    }

    private int scan(String s, int start, int stop, int step) {
        int open = 0;
        int close = 0;
        int best = 0;
        for (int index = start; index != stop; index += step) {
            if (s.charAt(index) == '(') {
                open++;
            } else {
                close++;
            }
            if (open == close) {
                best = Math.max(best, 2 * Math.min(open, close));
            } else if ((step == 1 && close > open) || (step == -1 && open > close)) {
                open = 0;
                close = 0;
            }
        }
        return best;
    }
}
