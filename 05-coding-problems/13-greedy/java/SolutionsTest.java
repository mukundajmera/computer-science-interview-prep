import java.util.Arrays;

public class SolutionsTest {
    public static void main(String[] args) {
        Solutions sol = new Solutions();
        int passed = 0;
        int total = 0;

        // maxSubArray
        total++; passed += sol.maxSubArray(new int[]{-2,1,-3,4,-1,2,1,-5,4}) == 6 ? 1 : 0;
        total++; passed += sol.maxSubArray(new int[]{1}) == 1 ? 1 : 0;
        total++; passed += sol.maxSubArray(new int[]{5,4,-1,7,8}) == 23 ? 1 : 0;
        total++; passed += sol.maxSubArray(new int[]{-1}) == -1 ? 1 : 0;
        total++; passed += sol.maxSubArray(new int[]{-2,-1}) == -1 ? 1 : 0;
        total++; passed += sol.maxSubArray(new int[]{2,1}) == 3 ? 1 : 0;

        // maxSubarraySumCircular
        total++; passed += sol.maxSubarraySumCircular(new int[]{1,-2,3,-2}) == 3 ? 1 : 0;
        total++; passed += sol.maxSubarraySumCircular(new int[]{5,-3,5}) == 10 ? 1 : 0;
        total++; passed += sol.maxSubarraySumCircular(new int[]{-3,-2,-3}) == -2 ? 1 : 0;
        total++; passed += sol.maxSubarraySumCircular(new int[]{3,-1,2,-1}) == 4 ? 1 : 0;
        total++; passed += sol.maxSubarraySumCircular(new int[]{3,-2,2,-3}) == 3 ? 1 : 0;
        total++; passed += sol.maxSubarraySumCircular(new int[]{-2,-3,-1}) == -1 ? 1 : 0;

        // canJump
        total++; passed += sol.canJump(new int[]{2,3,1,1,4}) ? 1 : 0;
        total++; passed += !sol.canJump(new int[]{3,2,1,0,4}) ? 1 : 0;
        total++; passed += sol.canJump(new int[]{0}) ? 1 : 0;
        total++; passed += sol.canJump(new int[]{1,2}) ? 1 : 0;
        total++; passed += sol.canJump(new int[]{2,0,0}) ? 1 : 0;
        total++; passed += !sol.canJump(new int[]{0,2,3}) ? 1 : 0;

        // jump
        total++; passed += sol.jump(new int[]{2,3,1,1,4}) == 2 ? 1 : 0;
        total++; passed += sol.jump(new int[]{2,3,0,1,4}) == 2 ? 1 : 0;
        total++; passed += sol.jump(new int[]{0}) == 0 ? 1 : 0;
        total++; passed += sol.jump(new int[]{1,2}) == 1 ? 1 : 0;
        total++; passed += sol.jump(new int[]{2,1,1,1,4}) == 3 ? 1 : 0;
        total++; passed += sol.jump(new int[]{1,1,1,1}) == 3 ? 1 : 0;

        // canCompleteCircuit
        total++; passed += sol.canCompleteCircuit(new int[]{1,2,3,4,5}, new int[]{3,4,5,1,2}) == 3 ? 1 : 0;
        total++; passed += sol.canCompleteCircuit(new int[]{2,3,4}, new int[]{3,4,3}) == -1 ? 1 : 0;
        total++; passed += sol.canCompleteCircuit(new int[]{5,1,2,3,4}, new int[]{4,4,1,5,1}) == 4 ? 1 : 0;
        total++; passed += sol.canCompleteCircuit(new int[]{3,1,1}, new int[]{1,2,2}) == 0 ? 1 : 0;
        total++; passed += sol.canCompleteCircuit(new int[]{1,1,3}, new int[]{2,2,1}) == 2 ? 1 : 0;
        total++; passed += sol.canCompleteCircuit(new int[]{2}, new int[]{2}) == 0 ? 1 : 0;

        // candy
        total++; passed += sol.candy(new int[]{1,0,2}) == 5 ? 1 : 0;
        total++; passed += sol.candy(new int[]{1,2,2}) == 4 ? 1 : 0;
        total++; passed += sol.candy(new int[]{1,3,2,2,1}) == 7 ? 1 : 0;
        total++; passed += sol.candy(new int[]{1,2,87,87,87,2,1}) == 13 ? 1 : 0;
        total++; passed += sol.candy(new int[]{1,2,3,4,5}) == 15 ? 1 : 0;
        total++; passed += sol.candy(new int[]{5,4,3,2,1}) == 15 ? 1 : 0;

        // nextPermutation
        int[] arr1 = {1,2,3}; sol.nextPermutation(arr1); total++; passed += Arrays.equals(arr1, new int[]{1,3,2}) ? 1 : 0;
        int[] arr2 = {3,2,1}; sol.nextPermutation(arr2); total++; passed += Arrays.equals(arr2, new int[]{1,2,3}) ? 1 : 0;
        int[] arr3 = {1,1,5}; sol.nextPermutation(arr3); total++; passed += Arrays.equals(arr3, new int[]{1,5,1}) ? 1 : 0;
        int[] arr4 = {1,3,2}; sol.nextPermutation(arr4); total++; passed += Arrays.equals(arr4, new int[]{2,1,3}) ? 1 : 0;
        int[] arr5 = {1}; sol.nextPermutation(arr5); total++; passed += Arrays.equals(arr5, new int[]{1}) ? 1 : 0;
        int[] arr6 = {2,3,1}; sol.nextPermutation(arr6); total++; passed += Arrays.equals(arr6, new int[]{3,1,2}) ? 1 : 0;

        System.out.println("Passed " + passed + " of " + total + " tests.");
        if (passed != total) {
            System.exit(1);
        }
    }
}
