public class SolutionsTest {
    public static void main(String[] args) {
        Solutions sol = new Solutions();
        
        // Test search
        assert sol.search(new int[]{-1,0,3,5,9,12}, 9) == 4;
        assert sol.search(new int[]{-1,0,3,5,9,12}, 2) == -1;
        assert sol.search(new int[]{5}, 5) == 0;
        assert sol.search(new int[]{5}, -5) == -1;
        assert sol.search(new int[]{}, 5) == -1;
        assert sol.search(new int[]{2, 5}, 5) == 1;

        // Test lowerBound
        assert sol.lowerBound(new int[]{1, 2, 2, 2, 3}, 2) == 1;
        assert sol.lowerBound(new int[]{1, 2, 2, 2, 3}, 4) == 5;
        assert sol.lowerBound(new int[]{1, 2, 2, 2, 3}, 0) == 0;
        assert sol.lowerBound(new int[]{2, 2, 2}, 2) == 0;
        assert sol.lowerBound(new int[]{}, 2) == 0;
        assert sol.lowerBound(new int[]{1}, 2) == 1;

        // Test searchInsert
        assert sol.searchInsert(new int[]{1,3,5,6}, 5) == 2;
        assert sol.searchInsert(new int[]{1,3,5,6}, 2) == 1;
        assert sol.searchInsert(new int[]{1,3,5,6}, 7) == 4;
        assert sol.searchInsert(new int[]{1,3,5,6}, 0) == 0;
        assert sol.searchInsert(new int[]{1}, 0) == 0;
        assert sol.searchInsert(new int[]{}, 0) == 0;

        // Test searchRotated
        assert sol.searchRotated(new int[]{4,5,6,7,0,1,2}, 0) == 4;
        assert sol.searchRotated(new int[]{4,5,6,7,0,1,2}, 3) == -1;
        assert sol.searchRotated(new int[]{1}, 0) == -1;
        assert sol.searchRotated(new int[]{1}, 1) == 0;
        assert sol.searchRotated(new int[]{2, 1}, 1) == 1;
        assert sol.searchRotated(new int[]{2, 1}, 2) == 0;

        // Test findMin
        assert sol.findMin(new int[]{3,4,5,1,2}) == 1;
        assert sol.findMin(new int[]{4,5,6,7,0,1,2}) == 0;
        assert sol.findMin(new int[]{11,13,15,17}) == 11;
        assert sol.findMin(new int[]{1}) == 1;
        assert sol.findMin(new int[]{2, 1}) == 1;
        assert sol.findMin(new int[]{1, 2}) == 1;

        // Test minEatingSpeed
        assert sol.minEatingSpeed(new int[]{3,6,7,11}, 8) == 4;
        assert sol.minEatingSpeed(new int[]{30,11,23,4,20}, 5) == 30;
        assert sol.minEatingSpeed(new int[]{30,11,23,4,20}, 6) == 23;
        assert sol.minEatingSpeed(new int[]{1}, 1) == 1;
        assert sol.minEatingSpeed(new int[]{1, 1}, 2) == 1;
        assert sol.minEatingSpeed(new int[]{10}, 1) == 10;

        // Test searchMatrix
        assert sol.searchMatrix(new int[][]{{1,3,5,7},{10,11,16,20},{23,30,34,60}}, 3) == true;
        assert sol.searchMatrix(new int[][]{{1,3,5,7},{10,11,16,20},{23,30,34,60}}, 13) == false;
        assert sol.searchMatrix(new int[][]{}, 0) == false;
        assert sol.searchMatrix(new int[][]{{}}, 0) == false;
        assert sol.searchMatrix(new int[][]{{1}}, 1) == true;
        assert sol.searchMatrix(new int[][]{{1}}, 0) == false;

        System.out.println("All Java tests passed!");
    }
}
