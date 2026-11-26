class Solution {
    public int calculateTime(String keyboard, String word) {
        int position = 0;
        int total = 0;
        for (int i = 0; i < word.length(); i++) {
            int next = keyboard.indexOf(word.charAt(i));
            total += Math.abs(next - position);
            position = next;
        }
        return total;
    }
}
