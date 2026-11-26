import java.util.ArrayList;
import java.util.LinkedHashSet;
import java.util.List;
import java.util.Set;

class Solution {
    public List<String> generateParenthesis(int n) {
        List<List<String>> dp = new ArrayList<>();
        dp.add(List.of(""));
        for (int pairs = 1; pairs <= n; pairs++) {
            Set<String> current = new LinkedHashSet<>();
            for (int left = 0; left < pairs; left++) {
                int right = pairs - 1 - left;
                for (String leftText : dp.get(left)) {
                    for (String rightText : dp.get(right)) {
                        current.add("(" + leftText + ")" + rightText);
                    }
                }
            }
            dp.add(new ArrayList<>(current));
        }
        return dp.get(n);
    }
}
