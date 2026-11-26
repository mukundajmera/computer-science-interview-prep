class Solution {
    public int minDistance(String word1, String word2) {
        if (word2.length() > word1.length()) {
            return minDistance(word2, word1);
        }
        int m = word1.length();
        int n = word2.length();
        int[] previous = new int[n + 1];
        for (int j = 0; j <= n; j++) {
            previous[j] = j;
        }
        for (int i = 1; i <= m; i++) {
            int[] current = new int[n + 1];
            current[0] = i;
            for (int j = 1; j <= n; j++) {
                if (word1.charAt(i - 1) == word2.charAt(j - 1)) {
                    current[j] = previous[j - 1];
                } else {
                    current[j] = 1 + Math.min(previous[j - 1], Math.min(previous[j], current[j - 1]));
                }
            }
            previous = current;
        }
        return previous[n];
    }
}
