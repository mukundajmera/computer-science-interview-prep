import java.util.HashMap;
import java.util.Map;

public class Solutions {

    public static class NumArray {
        private int[] prefix;

        public NumArray(int[] nums) {
            prefix = new int[nums.length + 1];
            for (int i = 0; i < nums.length; i++) {
                prefix[i + 1] = prefix[i] + nums[i];
            }
        }

        public int sumRange(int left, int right) {
            return prefix[right + 1] - prefix[left];
        }
    }

    public static int subarraySum(int[] nums, int k) {
        int count = 0;
        int currSum = 0;
        Map<Integer, Integer> prefixSums = new HashMap<>();
        prefixSums.put(0, 1);
        
        for (int num : nums) {
            currSum += num;
            if (prefixSums.containsKey(currSum - k)) {
                count += prefixSums.get(currSum - k);
            }
            prefixSums.put(currSum, prefixSums.getOrDefault(currSum, 0) + 1);
        }
        return count;
    }

    public static boolean checkSubarraySum(int[] nums, int k) {
        Map<Integer, Integer> remainderMap = new HashMap<>();
        remainderMap.put(0, -1);
        int currSum = 0;
        
        for (int i = 0; i < nums.length; i++) {
            currSum += nums[i];
            int remainder = currSum % k;
            
            if (remainderMap.containsKey(remainder)) {
                if (i - remainderMap.get(remainder) > 1) {
                    return true;
                }
            } else {
                remainderMap.put(remainder, i);
            }
        }
        return false;
    }

    public static class NumMatrix {
        private int[][] prefix;

        public NumMatrix(int[][] matrix) {
            if (matrix == null || matrix.length == 0 || matrix[0].length == 0) {
                return;
            }
            int m = matrix.length;
            int n = matrix[0].length;
            prefix = new int[m + 1][n + 1];
            
            for (int r = 0; r < m; r++) {
                for (int c = 0; c < n; c++) {
                    prefix[r + 1][c + 1] = matrix[r][c] + prefix[r][c + 1] + prefix[r + 1][c] - prefix[r][c];
                }
            }
        }

        public int sumRegion(int row1, int col1, int row2, int col2) {
            if (prefix == null) {
                return 0;
            }
            return prefix[row2 + 1][col2 + 1] - prefix[row1][col2 + 1] - prefix[row2 + 1][col1] + prefix[row1][col1];
        }
    }

    public static int pivotIndex(int[] nums) {
        int totalSum = 0;
        for (int num : nums) {
            totalSum += num;
        }
        
        int leftSum = 0;
        for (int i = 0; i < nums.length; i++) {
            if (leftSum == totalSum - leftSum - nums[i]) {
                return i;
            }
            leftSum += nums[i];
        }
        return -1;
    }

    public static int[] corpFlightBookings(int[][] bookings, int n) {
        int[] diff = new int[n];
        for (int[] booking : bookings) {
            int first = booking[0];
            int last = booking[1];
            int seats = booking[2];
            
            diff[first - 1] += seats;
            if (last < n) {
                diff[last] -= seats;
            }
        }
        
        for (int i = 1; i < n; i++) {
            diff[i] += diff[i - 1];
        }
        return diff;
    }
}
