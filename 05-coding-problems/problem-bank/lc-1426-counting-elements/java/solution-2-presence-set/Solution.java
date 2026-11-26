import java.util.HashSet;
import java.util.Set;

class Solution {
    public int countElements(int[] arr) {
        Set<Integer> values = new HashSet<>();
        for (int value : arr) values.add(value);
        int count = 0;
        for (int value : arr) if (values.contains(value + 1)) count++;
        return count;
    }
}
