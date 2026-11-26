class Solution {
    public int[] countBits(int n) {
        int[] answer = new int[n + 1];
        for (int value = 1; value <= n; value++) {
            answer[value] = answer[value >> 1] + (value & 1);
        }
        return answer;
    }
}
