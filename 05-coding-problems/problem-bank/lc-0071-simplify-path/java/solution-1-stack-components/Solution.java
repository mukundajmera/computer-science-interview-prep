import java.util.ArrayDeque;
import java.util.Deque;

class Solution {
    public String simplifyPath(String path) {
        Deque<String> stack = new ArrayDeque<>();
        for (String part : path.split("/")) {
            if (part.isEmpty() || part.equals(".")) {
                continue;
            }
            if (part.equals("..")) {
                if (!stack.isEmpty()) {
                    stack.removeLast();
                }
            } else {
                stack.addLast(part);
            }
        }
        if (stack.isEmpty()) {
            return "/";
        }
        StringBuilder builder = new StringBuilder();
        for (String part : stack) {
            builder.append('/').append(part);
        }
        return builder.toString();
    }
}
