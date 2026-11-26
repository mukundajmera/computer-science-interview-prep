import java.util.*;
class Solution {
    public List<String> restoreIpAddresses(String s) {
        List<String> result = new ArrayList<>();
        backtrack(s, 0, new ArrayList<>(), result);
        return result;
    }
    private void backtrack(String s, int index, List<String> parts, List<String> result) {
        int remainingParts = 4 - parts.size();
        int remainingDigits = s.length() - index;
        if (remainingDigits < remainingParts || remainingDigits > remainingParts * 3) return;
        if (parts.size() == 4) {
            if (index == s.length()) result.add(String.join(".", parts));
            return;
        }
        for (int end = index + 1; end <= Math.min(s.length(), index + 3); end++) {
            String part = s.substring(index, end);
            if (valid(part)) {
                parts.add(part);
                backtrack(s, end, parts, result);
                parts.remove(parts.size() - 1);
            }
        }
    }
    private boolean valid(String part) {
        if (part.length() > 1 && part.charAt(0) == '0') return false;
        return Integer.parseInt(part) <= 255;
    }
}
