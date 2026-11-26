import java.util.Arrays;

public class SolutionsTest {

    public static void assertEq(int expected, int actual, String msg) {
        if (expected != actual) {
            throw new AssertionError(msg + " | Expected: " + expected + ", Actual: " + actual);
        }
    }
    
    public static void assertEqArray(int[] expected, int[] actual, String msg) {
        if (!Arrays.equals(expected, actual)) {
            throw new AssertionError(msg + " | Expected: " + Arrays.toString(expected) + ", Actual: " + Arrays.toString(actual));
        }
    }

    public static void assertTrue(boolean condition, String msg) {
        if (!condition) {
            throw new AssertionError(msg + " | Expected true but got false");
        }
    }

    public static void assertFalse(boolean condition, String msg) {
        if (condition) {
            throw new AssertionError(msg + " | Expected false but got true");
        }
    }

    public static void main(String[] args) {
        testRangeSumQuery();
        testSubarraySum();
        testContinuousSubarraySum();
        testRangeSumQuery2D();
        testPivotIndex();
        testCorpFlightBookings();
        System.out.println("All Java tests passed!");
    }

    private static void testRangeSumQuery() {
        Solutions.NumArray obj = new Solutions.NumArray(new int[]{-2, 0, 3, -5, 2, -1});
        assertEq(1, obj.sumRange(0, 2), "RSQ 1");
        assertEq(-1, obj.sumRange(2, 5), "RSQ 2");
        assertEq(-3, obj.sumRange(0, 5), "RSQ 3");
        assertEq(0, obj.sumRange(1, 1), "RSQ 4");
        assertEq(-3, obj.sumRange(3, 4), "RSQ 5");
        
        Solutions.NumArray obj2 = new Solutions.NumArray(new int[]{1, 2, 3, 4, 5});
        assertEq(15, obj2.sumRange(0, 4), "RSQ 6");
    }

    private static void testSubarraySum() {
        assertEq(2, Solutions.subarraySum(new int[]{1, 1, 1}, 2), "SS 1");
        assertEq(2, Solutions.subarraySum(new int[]{1, 2, 3}, 3), "SS 2");
        assertEq(1, Solutions.subarraySum(new int[]{-1, -1, 1}, 0), "SS 3");
        assertEq(0, Solutions.subarraySum(new int[]{1}, 0), "SS 4");
        assertEq(3, Solutions.subarraySum(new int[]{-1, 1, 0}, 0), "SS 5");
        assertEq(4, Solutions.subarraySum(new int[]{3, 4, 7, 2, -3, 1, 4, 2}, 7), "SS 6");
    }

    private static void testContinuousSubarraySum() {
        assertTrue(Solutions.checkSubarraySum(new int[]{23, 2, 4, 6, 7}, 6), "CSS 1");
        assertTrue(Solutions.checkSubarraySum(new int[]{23, 2, 6, 4, 7}, 6), "CSS 2");
        assertFalse(Solutions.checkSubarraySum(new int[]{23, 2, 6, 4, 7}, 13), "CSS 3");
        assertTrue(Solutions.checkSubarraySum(new int[]{23, 2, 4, 6, 6}, 7), "CSS 4");
        assertFalse(Solutions.checkSubarraySum(new int[]{1, 0}, 2), "CSS 5");
        assertTrue(Solutions.checkSubarraySum(new int[]{5, 0, 0, 0}, 3), "CSS 6");
    }

    private static void testRangeSumQuery2D() {
        int[][] matrix = {
            {3, 0, 1, 4, 2},
            {5, 6, 3, 2, 1},
            {1, 2, 0, 1, 5},
            {4, 1, 0, 1, 7},
            {1, 0, 3, 0, 5}
        };
        Solutions.NumMatrix obj = new Solutions.NumMatrix(matrix);
        assertEq(8, obj.sumRegion(2, 1, 4, 3), "RSQ2D 1");
        assertEq(11, obj.sumRegion(1, 1, 2, 2), "RSQ2D 2");
        assertEq(12, obj.sumRegion(1, 2, 2, 4), "RSQ2D 3");
        assertEq(3, obj.sumRegion(0, 0, 0, 0), "RSQ2D 4");
        assertEq(58, obj.sumRegion(0, 0, 4, 4), "RSQ2D 5");
        
        Solutions.NumMatrix obj2 = new Solutions.NumMatrix(new int[][]{{1}});
        assertEq(1, obj2.sumRegion(0, 0, 0, 0), "RSQ2D 6");
    }

    private static void testPivotIndex() {
        assertEq(3, Solutions.pivotIndex(new int[]{1, 7, 3, 6, 5, 6}), "PI 1");
        assertEq(-1, Solutions.pivotIndex(new int[]{1, 2, 3}), "PI 2");
        assertEq(0, Solutions.pivotIndex(new int[]{2, 1, -1}), "PI 3");
        assertEq(0, Solutions.pivotIndex(new int[]{0, 0, 0}), "PI 4");
        assertEq(1, Solutions.pivotIndex(new int[]{0, 1, 0}), "PI 5");
        assertEq(0, Solutions.pivotIndex(new int[]{1, 0, 0}), "PI 6");
    }

    private static void testCorpFlightBookings() {
        assertEqArray(new int[]{10, 55, 45, 25, 25}, Solutions.corpFlightBookings(new int[][]{{1, 2, 10}, {2, 3, 20}, {2, 5, 25}}, 5), "CFB 1");
        assertEqArray(new int[]{10, 25}, Solutions.corpFlightBookings(new int[][]{{1, 2, 10}, {2, 2, 15}}, 2), "CFB 2");
        assertEqArray(new int[]{10}, Solutions.corpFlightBookings(new int[][]{{1, 1, 10}}, 1), "CFB 3");
        assertEqArray(new int[]{5, 15, 15, 10}, Solutions.corpFlightBookings(new int[][]{{1, 3, 5}, {2, 4, 10}}, 4), "CFB 4");
        assertEqArray(new int[]{5, 5, 0}, Solutions.corpFlightBookings(new int[][]{{1, 2, 5}}, 3), "CFB 5");
        assertEqArray(new int[]{0, 5, 5}, Solutions.corpFlightBookings(new int[][]{{2, 3, 5}}, 3), "CFB 6");
    }
}
