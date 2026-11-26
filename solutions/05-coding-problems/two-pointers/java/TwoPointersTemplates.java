import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;

/**
 * Minimal interview-grade two-pointer templates.
 *
 * Time/space notes are documented per method.
 */
public class TwoPointersTemplates {

    /** O(n) time, O(1) extra space. */
    public boolean hasPairSumSorted(int[] nums, int target) {
        int left = 0;
        int right = nums.length - 1;

        while (left < right) {
            int sum = nums[left] + nums[right];
            if (sum == target) {
                return true;
            }
            if (sum < target) {
                left++;
            } else {
                right--;
            }
        }

        return false;
    }

    /** O(n) time, O(1) extra space. */
    public int maxContainerArea(int[] heights) {
        int left = 0;
        int right = heights.length - 1;
        int best = 0;

        while (left < right) {
            int width = right - left;
            int area = Math.min(heights[left], heights[right]) * width;
            best = Math.max(best, area);

            if (heights[left] <= heights[right]) {
                left++;
            } else {
                right--;
            }
        }

        return best;
    }

    /** O(n^2) time after sort, O(1) auxiliary space excluding result. */
    public List<List<Integer>> threeSum(int[] nums) {
        Arrays.sort(nums);
        List<List<Integer>> result = new ArrayList<>();

        for (int i = 0; i < nums.length - 2; i++) {
            if (i > 0 && nums[i] == nums[i - 1]) {
                continue;
            }

            int left = i + 1;
            int right = nums.length - 1;

            while (left < right) {
                int total = nums[i] + nums[left] + nums[right];
                if (total == 0) {
                    result.add(Arrays.asList(nums[i], nums[left], nums[right]));
                    left++;
                    right--;
                    while (left < right && nums[left] == nums[left - 1]) {
                        left++;
                    }
                    while (left < right && nums[right] == nums[right + 1]) {
                        right--;
                    }
                } else if (total < 0) {
                    left++;
                } else {
                    right--;
                }
            }
        }

        return result;
    }

    /** O(n^2) time after sort, O(1) extra space. */
    public int countValidTriangles(int[] nums) {
        Arrays.sort(nums);
        int count = 0;

        for (int i = nums.length - 1; i >= 2; i--) {
            int left = 0;
            int right = i - 1;
            while (left < right) {
                if (nums[left] + nums[right] > nums[i]) {
                    count += right - left;
                    right--;
                } else {
                    left++;
                }
            }
        }

        return count;
    }

    /** O(n) time, O(1) extra space. */
    public void moveZeroes(int[] nums) {
        int write = 0;
        for (int scan = 0; scan < nums.length; scan++) {
            if (nums[scan] != 0) {
                int tmp = nums[write];
                nums[write] = nums[scan];
                nums[scan] = tmp;
                write++;
            }
        }
    }

    /** O(n) time, O(1) extra space. */
    public void sortColors(int[] nums) {
        int left = 0;
        int scan = 0;
        int right = nums.length - 1;

        while (scan <= right) {
            if (nums[scan] == 0) {
                swap(nums, left, scan);
                left++;
                scan++;
            } else if (nums[scan] == 1) {
                scan++;
            } else {
                swap(nums, scan, right);
                right--;
            }
        }
    }

    /** O(n) time, O(1) extra space. */
    public int trapRainWater(int[] heights) {
        if (heights.length == 0) {
            return 0;
        }

        int left = 0;
        int right = heights.length - 1;
        int leftMax = 0;
        int rightMax = 0;
        int trapped = 0;

        while (left <= right) {
            if (heights[left] <= heights[right]) {
                leftMax = Math.max(leftMax, heights[left]);
                trapped += leftMax - heights[left];
                left++;
            } else {
                rightMax = Math.max(rightMax, heights[right]);
                trapped += rightMax - heights[right];
                right--;
            }
        }

        return trapped;
    }

    private void swap(int[] nums, int i, int j) {
        int tmp = nums[i];
        nums[i] = nums[j];
        nums[j] = tmp;
    }
}
