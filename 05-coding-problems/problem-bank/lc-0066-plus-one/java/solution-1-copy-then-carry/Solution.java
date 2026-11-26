import java.util.Arrays;

class Solution {
    public int[] plusOne(int[] digits) {
        int[] result = Arrays.copyOf(digits, digits.length);
        int carry = 1;
        for (int index = result.length - 1; index >= 0 && carry > 0; index--) {
            int value = result[index] + carry;
            result[index] = value % 10;
            carry = value / 10;
        }
        if (carry == 0) {
            return result;
        }

        int[] expanded = new int[result.length + 1];
        expanded[0] = carry;
        return expanded;
    }
}
