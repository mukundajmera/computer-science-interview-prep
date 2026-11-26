class Solution {
    public String longestCommonPrefix(String[] strs) {
        if (strs.length == 0) {
            return "";
        }
        for (int index = 0; index < strs[0].length(); index++) {
            char expected = strs[0].charAt(index);
            for (int row = 1; row < strs.length; row++) {
                if (index == strs[row].length() || strs[row].charAt(index) != expected) {
                    return strs[0].substring(0, index);
                }
            }
        }
        return strs[0];
    }
}
