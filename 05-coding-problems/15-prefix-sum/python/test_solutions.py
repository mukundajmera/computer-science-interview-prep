import unittest
from solutions import NumArray, subarraySum, checkSubarraySum, NumMatrix, pivotIndex, corpFlightBookings

class TestPrefixSum(unittest.TestCase):
    def test_range_sum_query(self):
        obj = NumArray([-2, 0, 3, -5, 2, -1])
        self.assertEqual(obj.sumRange(0, 2), 1)
        self.assertEqual(obj.sumRange(2, 5), -1)
        self.assertEqual(obj.sumRange(0, 5), -3)
        self.assertEqual(obj.sumRange(1, 1), 0)
        self.assertEqual(obj.sumRange(3, 4), -3)
        
        obj2 = NumArray([1, 2, 3, 4, 5])
        self.assertEqual(obj2.sumRange(0, 4), 15)

    def test_subarray_sum(self):
        self.assertEqual(subarraySum([1, 1, 1], 2), 2)
        self.assertEqual(subarraySum([1, 2, 3], 3), 2)
        self.assertEqual(subarraySum([-1, -1, 1], 0), 1)
        self.assertEqual(subarraySum([1], 0), 0)
        self.assertEqual(subarraySum([-1, 1, 0], 0), 3)
        self.assertEqual(subarraySum([3, 4, 7, 2, -3, 1, 4, 2], 7), 4)

    def test_continuous_subarray_sum(self):
        self.assertTrue(checkSubarraySum([23, 2, 4, 6, 7], 6))
        self.assertTrue(checkSubarraySum([23, 2, 6, 4, 7], 6))
        self.assertFalse(checkSubarraySum([23, 2, 6, 4, 7], 13))
        self.assertTrue(checkSubarraySum([23, 2, 4, 6, 6], 7))
        self.assertFalse(checkSubarraySum([1, 0], 2))
        self.assertTrue(checkSubarraySum([5, 0, 0, 0], 3))

    def test_range_sum_query_2d(self):
        matrix = [
            [3, 0, 1, 4, 2],
            [5, 6, 3, 2, 1],
            [1, 2, 0, 1, 5],
            [4, 1, 0, 1, 7],
            [1, 0, 3, 0, 5]
        ]
        obj = NumMatrix(matrix)
        self.assertEqual(obj.sumRegion(2, 1, 4, 3), 8)
        self.assertEqual(obj.sumRegion(1, 1, 2, 2), 11)
        self.assertEqual(obj.sumRegion(1, 2, 2, 4), 12)
        self.assertEqual(obj.sumRegion(0, 0, 0, 0), 3)
        self.assertEqual(obj.sumRegion(0, 0, 4, 4), 58)
        
        obj2 = NumMatrix([[1]])
        self.assertEqual(obj2.sumRegion(0, 0, 0, 0), 1)

    def test_pivot_index(self):
        self.assertEqual(pivotIndex([1, 7, 3, 6, 5, 6]), 3)
        self.assertEqual(pivotIndex([1, 2, 3]), -1)
        self.assertEqual(pivotIndex([2, 1, -1]), 0)
        self.assertEqual(pivotIndex([0, 0, 0]), 0)
        self.assertEqual(pivotIndex([0, 1, 0]), 1)
        self.assertEqual(pivotIndex([1, 0, 0]), 0)

    def test_corp_flight_bookings(self):
        self.assertEqual(corpFlightBookings([[1, 2, 10], [2, 3, 20], [2, 5, 25]], 5), [10, 55, 45, 25, 25])
        self.assertEqual(corpFlightBookings([[1, 2, 10], [2, 2, 15]], 2), [10, 25])
        self.assertEqual(corpFlightBookings([[1, 1, 10]], 1), [10])
        self.assertEqual(corpFlightBookings([[1, 3, 5], [2, 4, 10]], 4), [5, 15, 15, 10])
        self.assertEqual(corpFlightBookings([[1, 2, 5]], 3), [5, 5, 0])
        self.assertEqual(corpFlightBookings([[2, 3, 5]], 3), [0, 5, 5])

if __name__ == '__main__':
    unittest.main()
