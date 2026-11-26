import java.util.*;
class Solution {
    public List<String> restoreIpAddresses(String s) {
        List<String> result = new ArrayList<>();
        for (int a = 1; a <= 3; a++)
            for (int b = 1; b <= 3; b++)
                for (int c = 1; c <= 3; c++)
                    for (int d = 1; d <= 3; d++)
                        if (a + b + c + d == s.length()) {
                            String p1 = s.substring(0, a), p2 = s.substring(a, a + b), p3 = s.substring(a + b, a + b + c), p4 = s.substring(a + b + c);
                            if (valid(p1) && valid(p2) && valid(p3) && valid(p4)) result.add(p1 + "." + p2 + "." + p3 + "." + p4);
                        }
        return result;
    }
    private boolean valid(String part) {
        if (part.length() > 1 && part.charAt(0) == '0') return false;
        int value = Integer.parseInt(part);
        return value <= 255;
    }
}
