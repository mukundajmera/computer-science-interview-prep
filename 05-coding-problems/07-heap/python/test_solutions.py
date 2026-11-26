import unittest
from solutions import Solution, ListNode, MedianFinder

class TestHeapSolutions(unittest.TestCase):
    def setUp(self):
        self.sol = Solution()

    def test_topKFrequent(self):
        self.assertEqual(sorted(self.sol.topKFrequent([1,1,1,2,2,3], 2)), [1, 2])
        self.assertEqual(self.sol.topKFrequent([1], 1), [1])

    def test_mergeKLists(self):
        l1 = ListNode(1, ListNode(4, ListNode(5)))
        l2 = ListNode(1, ListNode(3, ListNode(4)))
        l3 = ListNode(2, ListNode(6))
        res = self.sol.mergeKLists([l1, l2, l3])
        vals = []
        while res:
            vals.append(res.val)
            res = res.next
        self.assertEqual(vals, [1, 1, 2, 3, 4, 4, 5, 6])

    def test_MedianFinder(self):
        mf = MedianFinder()
        mf.addNum(1)
        mf.addNum(2)
        self.assertEqual(mf.findMedian(), 1.5)
        mf.addNum(3)
        self.assertEqual(mf.findMedian(), 2.0)

    def test_leastInterval(self):
        self.assertEqual(self.sol.leastInterval(["A","A","A","B","B","B"], 2), 8)
        self.assertEqual(self.sol.leastInterval(["A","A","A","B","B","B"], 0), 6)
        
    def test_findKthLargest(self):
        self.assertEqual(self.sol.findKthLargest([3,2,1,5,6,4], 2), 5)
        self.assertEqual(self.sol.findKthLargest([3,2,3,1,2,4,5,5,6], 4), 4)

    def test_kClosest(self):
        res1 = self.sol.kClosest([[1,3],[-2,2]], 1)
        self.assertEqual(len(res1), 1)
        self.assertIn([-2, 2], res1)
        
        res2 = self.sol.kClosest([[3,3],[5,-1],[-2,4]], 2)
        self.assertEqual(len(res2), 2)

    def test_findCheapestPrice(self):
        n = 4
        flights = [[0,1,100],[1,2,100],[2,0,100],[1,3,600],[2,3,200]]
        self.assertEqual(self.sol.findCheapestPrice(n, flights, 0, 3, 1), 700)
        self.assertEqual(self.sol.findCheapestPrice(3, [[0,1,100],[1,2,100],[0,2,500]], 0, 2, 1), 200)

if __name__ == '__main__':
    unittest.main()
