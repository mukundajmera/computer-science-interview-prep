import java.util.Random;

class Solution {
    private final int[] prefix;
    private final Random random = new Random(0);

    public Solution(int[] w) {
        prefix = new int[w.length];
        int total = 0;
        for (int i = 0; i < w.length; i++) {
            total += w[i];
            prefix[i] = total;
        }
    }

    public int pickIndex() {
        int target = random.nextInt(prefix[prefix.length - 1]) + 1;
        int left = 0;
        int right = prefix.length - 1;
        while (left < right) {
            int mid = left + (right - left) / 2;
            if (prefix[mid] >= target) {
                right = mid;
            } else {
                left = mid + 1;
            }
        }
        return left;
    }
}
