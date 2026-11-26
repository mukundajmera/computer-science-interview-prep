import unittest
from solutions import Solutions, ListNode, LRUCache

def build_list(vals):
    dummy = ListNode(0)
    curr = dummy
    for v in vals:
        curr.next = ListNode(v)
        curr = curr.next
    return dummy.next

def list_to_array(head):
    res = []
    while head:
        res.append(head.val)
        head = head.next
    return res

class TestSolutions(unittest.TestCase):
    def setUp(self):
        self.sol = Solutions()

    def test_reverseList(self):
        head = build_list([1, 2, 3, 4, 5])
        res = self.sol.reverseList(head)
        self.assertEqual(list_to_array(res), [5, 4, 3, 2, 1])

    def test_hasCycle(self):
        head = build_list([3, 2, 0, -4])
        head.next.next.next.next = head.next
        self.assertTrue(self.sol.hasCycle(head))
        self.assertFalse(self.sol.hasCycle(build_list([1, 2])))

    def test_mergeTwoLists(self):
        l1 = build_list([1, 2, 4])
        l2 = build_list([1, 3, 4])
        res = self.sol.mergeTwoLists(l1, l2)
        self.assertEqual(list_to_array(res), [1, 1, 2, 3, 4, 4])

    def test_middleNode(self):
        head = build_list([1, 2, 3, 4, 5])
        res = self.sol.middleNode(head)
        self.assertEqual(res.val, 3)
        head2 = build_list([1, 2, 3, 4, 5, 6])
        res2 = self.sol.middleNode(head2)
        self.assertEqual(res2.val, 4)

    def test_removeNthFromEnd(self):
        head = build_list([1, 2, 3, 4, 5])
        res = self.sol.removeNthFromEnd(head, 2)
        self.assertEqual(list_to_array(res), [1, 2, 3, 5])

    def test_isPalindrome(self):
        head = build_list([1, 2, 2, 1])
        self.assertTrue(self.sol.isPalindrome(head))
        head2 = build_list([1, 2])
        self.assertFalse(self.sol.isPalindrome(head2))

    def test_getIntersectionNode(self):
        headA = build_list([4, 1])
        headB = build_list([5, 6, 1])
        intersect = build_list([8, 4, 5])
        headA.next.next = intersect
        headB.next.next.next = intersect
        res = self.sol.getIntersectionNode(headA, headB)
        self.assertEqual(res.val, 8)

    def test_lru_cache(self):
        cache = LRUCache(2)
        cache.put(1, 1)
        cache.put(2, 2)
        self.assertEqual(cache.get(1), 1)
        cache.put(3, 3)
        self.assertEqual(cache.get(2), -1)
        cache.put(4, 4)
        self.assertEqual(cache.get(1), -1)
        self.assertEqual(cache.get(3), 3)
        self.assertEqual(cache.get(4), 4)

if __name__ == '__main__':
    unittest.main()
