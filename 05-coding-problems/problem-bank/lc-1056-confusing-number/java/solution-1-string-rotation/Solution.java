import java.util.HashMap;
import java.util.Map;

class Solution {
    public boolean confusingNumber(int n) {
        Map<Character, Character> map = new HashMap<>();
        map.put('0', '0'); map.put('1', '1'); map.put('6', '9'); map.put('8', '8'); map.put('9', '6');
        String value = String.valueOf(n);
        StringBuilder rotated = new StringBuilder();
        for (int i = value.length() - 1; i >= 0; i--) {
            char digit = value.charAt(i);
            if (!map.containsKey(digit)) {
                return false;
            }
            rotated.append(map.get(digit));
        }
        return !rotated.toString().equals(value);
    }
}
