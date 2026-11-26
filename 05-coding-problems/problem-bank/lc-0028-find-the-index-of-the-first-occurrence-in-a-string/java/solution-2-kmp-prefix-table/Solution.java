class Solution {
    public int strStr(String haystack, String needle) {
        if (needle.length() == 0) {
            return 0;
        }

        int[] lps = buildLps(needle);
        int matched = 0;
        for (int index = 0; index < haystack.length(); index++) {
            while (matched > 0 && haystack.charAt(index) != needle.charAt(matched)) {
                matched = lps[matched - 1];
            }
            if (haystack.charAt(index) == needle.charAt(matched)) {
                matched++;
                if (matched == needle.length()) {
                    return index - needle.length() + 1;
                }
            }
        }
        return -1;
    }

    private int[] buildLps(String pattern) {
        int[] lps = new int[pattern.length()];
        int length = 0;
        for (int index = 1; index < pattern.length(); index++) {
            while (length > 0 && pattern.charAt(index) != pattern.charAt(length)) {
                length = lps[length - 1];
            }
            if (pattern.charAt(index) == pattern.charAt(length)) {
                length++;
                lps[index] = length;
            }
        }
        return lps;
    }
}
