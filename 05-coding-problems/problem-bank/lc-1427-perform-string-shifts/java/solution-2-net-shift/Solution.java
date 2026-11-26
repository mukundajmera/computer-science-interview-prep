class Solution {
    public String stringShift(String s, int[][] shift) {
        int right = 0;
        for (int[] op : shift) right += op[0] == 1 ? op[1] : -op[1];
        right = ((right % s.length()) + s.length()) % s.length();
        if (right == 0) return s;
        return s.substring(s.length() - right) + s.substring(0, s.length() - right);
    }
}
