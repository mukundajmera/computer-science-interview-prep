import java.util.*;

public class SolutionsTest {
    public static void main(String[] args) {
        Solutions sol = new Solutions();
        
        // 1. Top K Frequent Elements
        int[] topKRes = sol.topKFrequent(new int[]{1,1,1,2,2,3}, 2);
        Arrays.sort(topKRes);
        assert Arrays.equals(topKRes, new int[]{1, 2}) : "Top K Frequent failed";

        // 2. Merge K Sorted Lists
        ListNode l1 = new ListNode(1, new ListNode(4, new ListNode(5)));
        ListNode l2 = new ListNode(1, new ListNode(3, new ListNode(4)));
        ListNode l3 = new ListNode(2, new ListNode(6));
        ListNode merged = sol.mergeKLists(new ListNode[]{l1, l2, l3});
        List<Integer> mergedVals = new ArrayList<>();
        while(merged != null) {
            mergedVals.add(merged.val);
            merged = merged.next;
        }
        assert mergedVals.equals(Arrays.asList(1, 1, 2, 3, 4, 4, 5, 6)) : "Merge K Lists failed";

        // 3. Find Median from Data Stream
        MedianFinder mf = new MedianFinder();
        mf.addNum(1);
        mf.addNum(2);
        assert mf.findMedian() == 1.5 : "MedianFinder failed 1";
        mf.addNum(3);
        assert mf.findMedian() == 2.0 : "MedianFinder failed 2";

        // 4. Task Scheduler
        assert sol.leastInterval(new char[]{'A','A','A','B','B','B'}, 2) == 8 : "Task Scheduler failed";

        // 5. Kth Largest Element in an Array
        assert sol.findKthLargest(new int[]{3,2,1,5,6,4}, 2) == 5 : "Kth Largest failed";

        // 6. K Closest Points to Origin
        int[][] kClosestRes = sol.kClosest(new int[][]{{1,3}, {-2,2}}, 1);
        assert kClosestRes.length == 1 && kClosestRes[0][0] == -2 && kClosestRes[0][1] == 2 : "K Closest failed";

        // 7. Cheapest Flights Within K Stops
        int[][] flights = {{0,1,100},{1,2,100},{2,0,100},{1,3,600},{2,3,200}};
        assert sol.findCheapestPrice(4, flights, 0, 3, 1) == 700 : "Cheapest Flights failed";

        System.out.println("All Java tests passed.");
    }
}
