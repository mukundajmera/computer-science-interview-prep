class Solution {
    public int[] replaceElements(int[] arr) {
        int[] result = new int[arr.length];
        for (int i = 0; i < arr.length; i++) {
            int best = -1;
            for (int j = i + 1; j < arr.length; j++) {
                best = Math.max(best, arr[j]);
            }
            result[i] = best;
        }
        return result;
    }
}
