class Solution {
    public boolean isInterleave(String s1, String s2, String s3) {
        if (s1.length() + s2.length() != s3.length()) {
            return false;
        }
        Boolean[][] memo = new Boolean[s1.length() + 1][s2.length() + 1];
        return canForm(s1, s2, s3, 0, 0, memo);
    }

    private boolean canForm(String s1, String s2, String s3, int i, int j, Boolean[][] memo) {
        if (i + j == s3.length()) {
            return true;
        }
        if (memo[i][j] != null) {
            return memo[i][j];
        }

        int target = i + j;
        boolean takeFirst = i < s1.length()
                && s1.charAt(i) == s3.charAt(target)
                && canForm(s1, s2, s3, i + 1, j, memo);
        boolean takeSecond = j < s2.length()
                && s2.charAt(j) == s3.charAt(target)
                && canForm(s1, s2, s3, i, j + 1, memo);
        memo[i][j] = takeFirst || takeSecond;
        return memo[i][j];
    }
}
