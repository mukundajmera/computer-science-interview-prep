class Solution {
    public int leastInterval(char[] tasks, int n) {
        int[] counts = new int[26];
        int maxFrequency = 0;
        for (char task : tasks) {
            int count = ++counts[task - 'A'];
            maxFrequency = Math.max(maxFrequency, count);
        }
        int maxCount = 0;
        for (int count : counts) {
            if (count == maxFrequency) {
                maxCount++;
            }
        }
        int framed = (maxFrequency - 1) * (n + 1) + maxCount;
        return Math.max(tasks.length, framed);
    }
}
