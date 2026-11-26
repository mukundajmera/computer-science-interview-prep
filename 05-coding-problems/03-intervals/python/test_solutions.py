import unittest
from solutions import Solutions

class TestIntervals(unittest.TestCase):
    def setUp(self):
        self.sol = Solutions()

    def test_merge(self):
        self.assertEqual(self.sol.merge([[1,3],[2,6],[8,10],[15,18]]), [[1,6],[8,10],[15,18]])
        self.assertEqual(self.sol.merge([[1,4],[4,5]]), [[1,5]])
        
    def test_insert(self):
        self.assertEqual(self.sol.insert([[1,3],[6,9]], [2,5]), [[1,5],[6,9]])
        self.assertEqual(self.sol.insert([[1,2],[3,5],[6,7],[8,10],[12,16]], [4,8]), [[1,2],[3,10],[12,16]])
        
    def test_eraseOverlapIntervals(self):
        self.assertEqual(self.sol.eraseOverlapIntervals([[1,2],[2,3],[3,4],[1,3]]), 1)
        self.assertEqual(self.sol.eraseOverlapIntervals([[1,2],[1,2],[1,2]]), 2)
        self.assertEqual(self.sol.eraseOverlapIntervals([[1,2],[2,3]]), 0)
        
    def test_canAttendMeetings(self):
        self.assertFalse(self.sol.canAttendMeetings([[0,30],[5,10],[15,20]]))
        self.assertTrue(self.sol.canAttendMeetings([[7,10],[2,4]]))
        
    def test_minMeetingRooms(self):
        self.assertEqual(self.sol.minMeetingRooms([[0,30],[5,10],[15,20]]), 2)
        self.assertEqual(self.sol.minMeetingRooms([[7,10],[2,4]]), 1)
        
    def test_findMinArrowShots(self):
        self.assertEqual(self.sol.findMinArrowShots([[10,16],[2,8],[1,6],[7,12]]), 2)
        self.assertEqual(self.sol.findMinArrowShots([[1,2],[3,4],[5,6],[7,8]]), 4)
        
    def test_intervalIntersection(self):
        self.assertEqual(self.sol.intervalIntersection([[0,2],[5,10],[13,23],[24,25]], [[1,5],[8,12],[15,24],[25,26]]), [[1,2],[5,5],[8,10],[15,23],[24,24],[25,25]])
        self.assertEqual(self.sol.intervalIntersection([[1,3],[5,9]], []), [])
        self.assertEqual(self.sol.intervalIntersection([], [[4,8],[10,12]]), [])

if __name__ == '__main__':
    unittest.main()
