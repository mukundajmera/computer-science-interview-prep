class Solution {
    public int romanToInt(String s) {
        int total = 0;
        int maxRight = 0;
        for (int i = s.length() - 1; i >= 0; i--) {
            int value = valueOf(s.charAt(i));
            if (value < maxRight) {
                total -= value;
            } else {
                total += value;
                maxRight = value;
            }
        }
        return total;
    }

    private int valueOf(char symbol) {
        if (symbol == 'I') return 1;
        if (symbol == 'V') return 5;
        if (symbol == 'X') return 10;
        if (symbol == 'L') return 50;
        if (symbol == 'C') return 100;
        if (symbol == 'D') return 500;
        return 1000;
    }
}
