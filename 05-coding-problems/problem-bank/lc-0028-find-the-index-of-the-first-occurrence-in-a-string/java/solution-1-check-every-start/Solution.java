class Solution {
    public int strStr(String haystack, String needle) {
        int n = haystack.length();
        int m = needle.length();
        for (int start = 0; start <= n - m; start++) {
            int offset = 0;
            while (offset < m && haystack.charAt(start + offset) == needle.charAt(offset)) {
                offset++;
            }
            if (offset == m) {
                return start;
            }
        }
        return -1;
    }
}
