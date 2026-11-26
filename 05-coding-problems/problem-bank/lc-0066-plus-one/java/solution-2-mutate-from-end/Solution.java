class Solution {
    public int[] plusOne(int[] digits) {
        for (int index = digits.length - 1; index >= 0; index--) {
            if (digits[index] < 9) {
                digits[index]++;
                return digits;
            }
            digits[index] = 0;
        }

        int[] expanded = new int[digits.length + 1];
        expanded[0] = 1;
        return expanded;
    }
}
