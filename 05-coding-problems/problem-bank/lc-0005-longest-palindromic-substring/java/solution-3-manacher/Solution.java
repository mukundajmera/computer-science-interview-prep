class Solution {
    public String longestPalindrome(String s) {
        if (s.length() < 2) {
            return s;
        }

        char[] transformed = new char[s.length() * 2 + 3];
        transformed[0] = '^';
        int index = 1;
        for (int i = 0; i < s.length(); i++) {
            transformed[index++] = '#';
            transformed[index++] = s.charAt(i);
        }
        transformed[index++] = '#';
        transformed[index] = '$';

        int[] radius = new int[transformed.length];
        int center = 0;
        int right = 0;
        int bestCenter = 0;
        int bestRadius = 0;

        for (int i = 1; i < transformed.length - 1; i++) {
            int mirror = 2 * center - i;
            if (i < right) {
                radius[i] = Math.min(right - i, radius[mirror]);
            }
            while (transformed[i + radius[i] + 1] == transformed[i - radius[i] - 1]) {
                radius[i]++;
            }
            if (i + radius[i] > right) {
                center = i;
                right = i + radius[i];
            }
            if (radius[i] > bestRadius) {
                bestRadius = radius[i];
                bestCenter = i;
            }
        }

        int start = (bestCenter - bestRadius) / 2;
        return s.substring(start, start + bestRadius);
    }
}
