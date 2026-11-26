class Solution {
    public int countElements(int[] arr) {
        int count = 0;
        for (int value : arr) {
            for (int candidate : arr) {
                if (candidate == value + 1) {
                    count++;
                    break;
                }
            }
        }
        return count;
    }
}
