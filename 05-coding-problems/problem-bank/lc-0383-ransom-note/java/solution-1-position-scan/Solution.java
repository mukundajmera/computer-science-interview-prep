class Solution {
    public boolean canConstruct(String ransomNote, String magazine) {
        boolean[] used = new boolean[magazine.length()];
        for (int i = 0; i < ransomNote.length(); i++) {
            char needed = ransomNote.charAt(i);
            boolean matched = false;
            for (int j = 0; j < magazine.length(); j++) {
                if (!used[j] && magazine.charAt(j) == needed) {
                    used[j] = true;
                    matched = true;
                    break;
                }
            }
            if (!matched) {
                return false;
            }
        }
        return true;
    }
}
