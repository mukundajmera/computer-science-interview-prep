class Solution {
    public boolean isPalindrome(int x) {
        if (x < 0) {
            return false;
        }
        String text = Integer.toString(x);
        int left = 0;
        int right = text.length() - 1;
        while (left < right) {
            if (text.charAt(left) != text.charAt(right)) {
                return false;
            }
            left++;
            right--;
        }
        return true;
    }
}
