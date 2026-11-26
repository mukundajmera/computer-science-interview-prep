class Solution {
    public int calculateTime(String keyboard, String word) {
        int[] positions = new int[26];
        for (int i = 0; i < keyboard.length(); i++) {
            positions[keyboard.charAt(i) - 'a'] = i;
        }
        int current = 0;
        int total = 0;
        for (int i = 0; i < word.length(); i++) {
            int next = positions[word.charAt(i) - 'a'];
            total += Math.abs(next - current);
            current = next;
        }
        return total;
    }
}
