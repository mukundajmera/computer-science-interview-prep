class Solution {
    public int reverseBits(int n) {
        int result = 0;
        int value = n;
        for (int i = 0; i < 32; i++) {
            result = (result << 1) | (value & 1);
            value >>>= 1;
        }
        return result;
    }
}
