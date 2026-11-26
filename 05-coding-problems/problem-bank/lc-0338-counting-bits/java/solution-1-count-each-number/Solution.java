class Solution {
    public int[] countBits(int n) {
        int[] answer = new int[n + 1];
        for (int value = 0; value <= n; value++) {
            int current = value;
            int count = 0;
            while (current != 0) {
                current &= current - 1;
                count++;
            }
            answer[value] = count;
        }
        return answer;
    }
}
