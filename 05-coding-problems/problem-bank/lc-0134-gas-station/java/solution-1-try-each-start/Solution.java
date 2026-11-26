class Solution {
    public int canCompleteCircuit(int[] gas, int[] cost) {
        int n = gas.length;
        for (int start = 0; start < n; start++) {
            int tank = 0;
            boolean completed = true;
            for (int step = 0; step < n; step++) {
                int index = (start + step) % n;
                tank += gas[index] - cost[index];
                if (tank < 0) {
                    completed = false;
                    break;
                }
            }
            if (completed) {
                return start;
            }
        }
        return -1;
    }
}
