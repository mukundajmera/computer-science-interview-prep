class Solution {
    public String longestPalindrome(String s) {
        int n = s.length();
        for (int length = n; length >= 1; length--) {
            for (int start = 0; start + length <= n; start++) {
                if (isPalindrome(s, start, start + length - 1)) {
                    return s.substring(start, start + length);
                }
            }
        }
        return "";
    }

    private boolean isPalindrome(String s, int left, int right) {
        while (left < right) {
            if (s.charAt(left) != s.charAt(right)) {
                return false;
            }
            left++;
            right--;
        }
        return true;
    }
}
