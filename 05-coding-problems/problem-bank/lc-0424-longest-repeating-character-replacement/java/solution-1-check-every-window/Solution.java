class Solution {
    public int characterReplacement(String s, int k) {
        int best = 0;
        for (int start = 0; start < s.length(); start++) {
            int[] counts = new int[26];
            int maxCount = 0;
            for (int end = start; end < s.length(); end++) {
                int index = s.charAt(end) - 'A';
                counts[index]++;
                maxCount = Math.max(maxCount, counts[index]);
                int length = end - start + 1;
                if (length - maxCount <= k) {
                    best = Math.max(best, length);
                }
            }
        }
        return best;
    }
}
