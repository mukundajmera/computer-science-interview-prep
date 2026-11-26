import unittest


class TestV2(unittest.TestCase):
    def test_v2_sanity(self) -> None:
        self.assertEqual(2, 1 + 1)


if __name__ == "__main__":
    unittest.main()
