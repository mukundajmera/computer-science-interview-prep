import java.util.*;

public class SolutionsTest {
    private static void assertEqual(int expected, int actual) {
        if (expected != actual) {
            throw new AssertionError("Expected " + expected + " but got " + actual);
        }
    }
    
    private static void assertTrue(boolean condition) {
        if (!condition) {
            throw new AssertionError("Expected true but got false");
        }
    }

    private static void assertFalse(boolean condition) {
        if (condition) {
            throw new AssertionError("Expected false but got true");
        }
    }
    
    private static void assertArrayEqual(int[] expected, int[] actual) {
        if (!Arrays.equals(expected, actual)) {
            throw new AssertionError("Expected " + Arrays.toString(expected) + " but got " + Arrays.toString(actual));
        }
    }

    public static ListNode buildList(int[] vals) {
        ListNode dummy = new ListNode(0);
        ListNode curr = dummy;
        for (int v : vals) {
            curr.next = new ListNode(v);
            curr = curr.next;
        }
        return dummy.next;
    }

    public static int[] listToArray(ListNode head) {
        List<Integer> res = new ArrayList<>();
        while (head != null) {
            res.add(head.val);
            head = head.next;
        }
        return res.stream().mapToInt(i -> i).toArray();
    }

    public static void main(String[] args) {
        Solutions sol = new Solutions();

        // test_reverseList
        ListNode head1 = buildList(new int[]{1, 2, 3, 4, 5});
        ListNode res1 = sol.reverseList(head1);
        assertArrayEqual(new int[]{5, 4, 3, 2, 1}, listToArray(res1));

        // test_hasCycle
        ListNode head2 = buildList(new int[]{3, 2, 0, -4});
        head2.next.next.next.next = head2.next;
        assertTrue(sol.hasCycle(head2));
        assertFalse(sol.hasCycle(buildList(new int[]{1, 2})));

        // test_mergeTwoLists
        ListNode l1 = buildList(new int[]{1, 2, 4});
        ListNode l2 = buildList(new int[]{1, 3, 4});
        ListNode res3 = sol.mergeTwoLists(l1, l2);
        assertArrayEqual(new int[]{1, 1, 2, 3, 4, 4}, listToArray(res3));

        // test_middleNode
        ListNode head4 = buildList(new int[]{1, 2, 3, 4, 5});
        ListNode res4 = sol.middleNode(head4);
        assertEqual(3, res4.val);
        ListNode head5 = buildList(new int[]{1, 2, 3, 4, 5, 6});
        ListNode res5 = sol.middleNode(head5);
        assertEqual(4, res5.val);

        // test_removeNthFromEnd
        ListNode head6 = buildList(new int[]{1, 2, 3, 4, 5});
        ListNode res6 = sol.removeNthFromEnd(head6, 2);
        assertArrayEqual(new int[]{1, 2, 3, 5}, listToArray(res6));

        // test_isPalindrome
        ListNode head7 = buildList(new int[]{1, 2, 2, 1});
        assertTrue(sol.isPalindrome(head7));
        ListNode head8 = buildList(new int[]{1, 2});
        assertFalse(sol.isPalindrome(head8));

        // test_getIntersectionNode
        ListNode headA = buildList(new int[]{4, 1});
        ListNode headB = buildList(new int[]{5, 6, 1});
        ListNode intersect = buildList(new int[]{8, 4, 5});
        headA.next.next = intersect;
        headB.next.next.next = intersect;
        ListNode res9 = sol.getIntersectionNode(headA, headB);
        assertEqual(8, res9.val);

        // test_lru_cache
        LRUCache cache = new LRUCache(2);
        cache.put(1, 1);
        cache.put(2, 2);
        assertEqual(1, cache.get(1));
        cache.put(3, 3);
        assertEqual(-1, cache.get(2));
        cache.put(4, 4);
        assertEqual(-1, cache.get(1));
        assertEqual(3, cache.get(3));
        assertEqual(4, cache.get(4));
        
        System.out.println("All tests passed!");
    }
}
