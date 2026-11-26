import java.util.Arrays;
import java.util.List;

public class SolutionsTest {
    public static void main(String[] args) {
        Solutions sol = new Solutions();
        
        // test_maxArea
        assert sol.maxArea(new int[]{1,8,6,2,5,4,8,3,7}) == 49;
        assert sol.maxArea(new int[]{1,1}) == 1;
        assert sol.maxArea(new int[]{4,3,2,1,4}) == 16;
        assert sol.maxArea(new int[]{1,2,1}) == 2;
        assert sol.maxArea(new int[]{0,0}) == 0;
        assert sol.maxArea(new int[]{10,9,8,7,6,5,4,3,2,1}) == 25;
        
        // test_twoSum
        assert Arrays.equals(sol.twoSum(new int[]{2,7,11,15}, 9), new int[]{1,2});
        assert Arrays.equals(sol.twoSum(new int[]{2,3,4}, 6), new int[]{1,3});
        assert Arrays.equals(sol.twoSum(new int[]{-1,0}, -1), new int[]{1,2});
        assert Arrays.equals(sol.twoSum(new int[]{1,2,3,4,4,9,56,90}, 8), new int[]{4,5});
        assert Arrays.equals(sol.twoSum(new int[]{1,1}, 2), new int[]{1,2});
        assert Arrays.equals(sol.twoSum(new int[]{-5,-2,-1,0,3}, -2), new int[]{1,5});
        
        // test_threeSum
        assert sol.threeSum(new int[]{-1,0,1,2,-1,-4}).equals(Arrays.asList(Arrays.asList(-1,-1,2), Arrays.asList(-1,0,1)));
        assert sol.threeSum(new int[]{0,1,1}).equals(Arrays.asList());
        assert sol.threeSum(new int[]{0,0,0}).equals(Arrays.asList(Arrays.asList(0,0,0)));
        assert sol.threeSum(new int[]{-2,0,0,2,2}).equals(Arrays.asList(Arrays.asList(-2,0,2)));
        assert sol.threeSum(new int[]{0,0,0,0}).equals(Arrays.asList(Arrays.asList(0,0,0)));
        assert sol.threeSum(new int[]{-1,0,1,0}).equals(Arrays.asList(Arrays.asList(-1,0,1)));
        
        // test_triangleNumber
        assert sol.triangleNumber(new int[]{2,2,3,4}) == 3;
        assert sol.triangleNumber(new int[]{4,2,3,4}) == 4;
        assert sol.triangleNumber(new int[]{0,0,0}) == 0;
        assert sol.triangleNumber(new int[]{1,1,1,1}) == 4;
        assert sol.triangleNumber(new int[]{1,2,3,4,5,6}) == 7;
        assert sol.triangleNumber(new int[]{7,0,0,0}) == 0;
        
        // test_moveZeroes
        int[] arr1 = {0,1,0,3,12}; sol.moveZeroes(arr1); assert Arrays.equals(arr1, new int[]{1,3,12,0,0});
        int[] arr2 = {0}; sol.moveZeroes(arr2); assert Arrays.equals(arr2, new int[]{0});
        int[] arr3 = {1,2,3}; sol.moveZeroes(arr3); assert Arrays.equals(arr3, new int[]{1,2,3});
        int[] arr4 = {0,0,1}; sol.moveZeroes(arr4); assert Arrays.equals(arr4, new int[]{1,0,0});
        int[] arr5 = {1,0,0}; sol.moveZeroes(arr5); assert Arrays.equals(arr5, new int[]{1,0,0});
        int[] arr6 = {4,2,4,0,0,3,0,5,1,0}; sol.moveZeroes(arr6); assert Arrays.equals(arr6, new int[]{4,2,4,3,5,1,0,0,0,0});
        
        // test_sortColors
        int[] c1 = {2,0,2,1,1,0}; sol.sortColors(c1); assert Arrays.equals(c1, new int[]{0,0,1,1,2,2});
        int[] c2 = {2,0,1}; sol.sortColors(c2); assert Arrays.equals(c2, new int[]{0,1,2});
        int[] c3 = {0}; sol.sortColors(c3); assert Arrays.equals(c3, new int[]{0});
        int[] c4 = {1}; sol.sortColors(c4); assert Arrays.equals(c4, new int[]{1});
        int[] c5 = {2}; sol.sortColors(c5); assert Arrays.equals(c5, new int[]{2});
        int[] c6 = {2,2,2,1,1,1,0,0,0}; sol.sortColors(c6); assert Arrays.equals(c6, new int[]{0,0,0,1,1,1,2,2,2});
        
        // test_trap
        assert sol.trap(new int[]{0,1,0,2,1,0,1,3,2,1,2,1}) == 6;
        assert sol.trap(new int[]{4,2,0,3,2,5}) == 9;
        assert sol.trap(new int[]{0,0,0}) == 0;
        assert sol.trap(new int[]{3,0,3}) == 3;
        assert sol.trap(new int[]{1,2,3,4}) == 0;
        assert sol.trap(new int[]{4,3,2,1}) == 0;

        System.out.println("All Java tests passed.");
    }
}
