class Solution {
    private String text;
    private String pattern;
    private Boolean[][] memo;

    public boolean isMatch(String s, String p) {
        text = s;
        pattern = p;
        memo = new Boolean[s.length() + 1][p.length() + 1];
        return matches(0, 0);
    }

    private boolean matches(int i, int j) {
        if (memo[i][j] != null) return memo[i][j];
        if (j == pattern.length()) {
            memo[i][j] = i == text.length();
            return memo[i][j];
        }
        boolean first = i < text.length()
            && (pattern.charAt(j) == text.charAt(i) || pattern.charAt(j) == '.');
        if (j + 1 < pattern.length() && pattern.charAt(j + 1) == '*') {
            memo[i][j] = matches(i, j + 2) || (first && matches(i + 1, j));
        } else {
            memo[i][j] = first && matches(i + 1, j + 1);
        }
        return memo[i][j];
    }
}
