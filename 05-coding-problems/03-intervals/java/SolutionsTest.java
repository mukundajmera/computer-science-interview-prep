import java.util.Arrays;

public class SolutionsTest {
    public static void main(String[] args) {
        Solutions sol = new Solutions();
        int failed = 0;

        // Test merge
        int[][] resMerge1 = sol.merge(new int[][]{{1,3},{2,6},{8,10},{15,18}});
        if (!Arrays.deepEquals(resMerge1, new int[][]{{1,6},{8,10},{15,18}})) {
            System.out.println("Test merge 1 failed");
            failed++;
        }
        
        int[][] resMerge2 = sol.merge(new int[][]{{1,4},{4,5}});
        if (!Arrays.deepEquals(resMerge2, new int[][]{{1,5}})) {
            System.out.println("Test merge 2 failed");
            failed++;
        }

        // Test insert
        int[][] resInsert1 = sol.insert(new int[][]{{1,3},{6,9}}, new int[]{2,5});
        if (!Arrays.deepEquals(resInsert1, new int[][]{{1,5},{6,9}})) {
            System.out.println("Test insert 1 failed");
            failed++;
        }
        
        int[][] resInsert2 = sol.insert(new int[][]{{1,2},{3,5},{6,7},{8,10},{12,16}}, new int[]{4,8});
        if (!Arrays.deepEquals(resInsert2, new int[][]{{1,2},{3,10},{12,16}})) {
            System.out.println("Test insert 2 failed");
            failed++;
        }

        // Test eraseOverlapIntervals
        if (sol.eraseOverlapIntervals(new int[][]{{1,2},{2,3},{3,4},{1,3}}) != 1) {
            System.out.println("Test eraseOverlapIntervals 1 failed");
            failed++;
        }
        
        if (sol.eraseOverlapIntervals(new int[][]{{1,2},{1,2},{1,2}}) != 2) {
            System.out.println("Test eraseOverlapIntervals 2 failed");
            failed++;
        }

        if (sol.eraseOverlapIntervals(new int[][]{{1,2},{2,3}}) != 0) {
            System.out.println("Test eraseOverlapIntervals 3 failed");
            failed++;
        }

        // Test canAttendMeetings
        if (sol.canAttendMeetings(new int[][]{{0,30},{5,10},{15,20}})) {
            System.out.println("Test canAttendMeetings 1 failed");
            failed++;
        }
        
        if (!sol.canAttendMeetings(new int[][]{{7,10},{2,4}})) {
            System.out.println("Test canAttendMeetings 2 failed");
            failed++;
        }

        // Test minMeetingRooms
        if (sol.minMeetingRooms(new int[][]{{0,30},{5,10},{15,20}}) != 2) {
            System.out.println("Test minMeetingRooms 1 failed");
            failed++;
        }
        
        if (sol.minMeetingRooms(new int[][]{{7,10},{2,4}}) != 1) {
            System.out.println("Test minMeetingRooms 2 failed");
            failed++;
        }

        // Test findMinArrowShots
        if (sol.findMinArrowShots(new int[][]{{10,16},{2,8},{1,6},{7,12}}) != 2) {
            System.out.println("Test findMinArrowShots 1 failed");
            failed++;
        }
        
        if (sol.findMinArrowShots(new int[][]{{1,2},{3,4},{5,6},{7,8}}) != 4) {
            System.out.println("Test findMinArrowShots 2 failed");
            failed++;
        }

        // Test intervalIntersection
        int[][] resInter1 = sol.intervalIntersection(new int[][]{{0,2},{5,10},{13,23},{24,25}}, new int[][]{{1,5},{8,12},{15,24},{25,26}});
        if (!Arrays.deepEquals(resInter1, new int[][]{{1,2},{5,5},{8,10},{15,23},{24,24},{25,25}})) {
            System.out.println("Test intervalIntersection 1 failed");
            failed++;
        }
        
        int[][] resInter2 = sol.intervalIntersection(new int[][]{{1,3},{5,9}}, new int[][]{});
        if (!Arrays.deepEquals(resInter2, new int[][]{})) {
            System.out.println("Test intervalIntersection 2 failed");
            failed++;
        }

        int[][] resInter3 = sol.intervalIntersection(new int[][]{}, new int[][]{{4,8},{10,12}});
        if (!Arrays.deepEquals(resInter3, new int[][]{})) {
            System.out.println("Test intervalIntersection 3 failed");
            failed++;
        }

        if (failed == 0) {
            System.out.println("All tests passed!");
        } else {
            System.out.println(failed + " tests failed.");
            System.exit(1);
        }
    }
}
