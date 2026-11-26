class Solution {
    public String multiply(String num1, String num2) {
        if (num1.equals("0") || num2.equals("0")) return "0";
        String result = "0";
        String zeros = "";
        for (int i = num2.length() - 1; i >= 0; i--) {
            String partial = multiplyByDigit(num1, num2.charAt(i) - '0') + zeros;
            result = add(result, partial);
            zeros += "0";
        }
        return stripLeadingZeros(result);
    }

    private String multiplyByDigit(String value, int digit) {
        StringBuilder builder = new StringBuilder();
        int carry = 0;
        for (int i = value.length() - 1; i >= 0; i--) {
            int product = (value.charAt(i) - '0') * digit + carry;
            builder.append(product % 10);
            carry = product / 10;
        }
        if (carry > 0) builder.append(carry);
        return builder.reverse().toString();
    }

    private String add(String a, String b) {
        StringBuilder builder = new StringBuilder();
        int i = a.length() - 1;
        int j = b.length() - 1;
        int carry = 0;
        while (i >= 0 || j >= 0 || carry > 0) {
            int total = carry;
            if (i >= 0) total += a.charAt(i--) - '0';
            if (j >= 0) total += b.charAt(j--) - '0';
            builder.append(total % 10);
            carry = total / 10;
        }
        return builder.reverse().toString();
    }

    private String stripLeadingZeros(String value) {
        int index = 0;
        while (index < value.length() - 1 && value.charAt(index) == '0') index++;
        return value.substring(index);
    }
}
