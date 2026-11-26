class Solution {
    private String best;

    public String largestNumber(int[] nums) {
        String[] values = new String[nums.length];
        for (int i = 0; i < nums.length; i++) {
            values[i] = String.valueOf(nums[i]);
        }
        best = "";
        boolean[] used = new boolean[values.length];
        permute(values, used, new StringBuilder(), 0);
        return best.charAt(0) == '0' ? "0" : best;
    }

    private void permute(String[] values, boolean[] used, StringBuilder current, int depth) {
        if (depth == values.length) {
            String candidate = current.toString();
            if (candidate.compareTo(best) > 0) {
                best = candidate;
            }
            return;
        }
        for (int i = 0; i < values.length; i++) {
            if (used[i]) {
                continue;
            }
            used[i] = true;
            int length = current.length();
            current.append(values[i]);
            permute(values, used, current, depth + 1);
            current.setLength(length);
            used[i] = false;
        }
    }
}
