class Solution {
    public String stringShift(String s, int[][] shift) {
        String current = s;
        for (int[] op : shift) {
            int amount = op[1] % current.length();
            if (op[0] == 0) current = current.substring(amount) + current.substring(0, amount);
            else current = current.substring(current.length() - amount) + current.substring(0, current.length() - amount);
        }
        return current;
    }
}
