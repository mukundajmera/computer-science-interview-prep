import java.util.Arrays;

class Solution {
    public String largestNumber(int[] nums) {
        String[] values = new String[nums.length];
        for (int i = 0; i < nums.length; i++) {
            values[i] = String.valueOf(nums[i]);
        }
        Arrays.sort(values, (left, right) -> (right + left).compareTo(left + right));
        if (values[0].equals("0")) {
            return "0";
        }
        StringBuilder answer = new StringBuilder();
        for (String value : values) {
            answer.append(value);
        }
        return answer.toString();
    }
}
