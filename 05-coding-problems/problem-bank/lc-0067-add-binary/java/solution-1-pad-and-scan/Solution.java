class Solution {
    public String addBinary(String a, String b) {
        int maxLength = Math.max(a.length(), b.length());
        String left = "0".repeat(maxLength - a.length()) + a;
        String right = "0".repeat(maxLength - b.length()) + b;
        StringBuilder reversed = new StringBuilder();
        int carry = 0;
        for (int i = maxLength - 1; i >= 0; i--) {
            int sum = carry + (left.charAt(i) - '0') + (right.charAt(i) - '0');
            reversed.append(sum % 2);
            carry = sum / 2;
        }
        if (carry > 0) {
            reversed.append(carry);
        }
        return reversed.reverse().toString();
    }
}
