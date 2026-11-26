import java.util.ArrayDeque;
import java.util.Deque;

class Solution {
    public String decodeString(String s) {
        Deque<StringBuilder> builders = new ArrayDeque<>();
        Deque<Integer> counts = new ArrayDeque<>();
        StringBuilder current = new StringBuilder();
        int repeat = 0;
        for (int i = 0; i < s.length(); i++) {
            char ch = s.charAt(i);
            if (Character.isDigit(ch)) {
                repeat = repeat * 10 + (ch - '0');
            } else if (ch == '[') {
                builders.push(current);
                counts.push(repeat);
                current = new StringBuilder();
                repeat = 0;
            } else if (ch == ']') {
                StringBuilder parent = builders.pop();
                int times = counts.pop();
                for (int count = 0; count < times; count++) {
                    parent.append(current);
                }
                current = parent;
            } else {
                current.append(ch);
            }
        }
        return current.toString();
    }
}
