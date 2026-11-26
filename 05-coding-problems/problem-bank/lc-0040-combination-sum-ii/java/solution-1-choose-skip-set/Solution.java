import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashSet;
import java.util.List;
import java.util.Set;

class Solution {
    public List<List<Integer>> combinationSum2(int[] candidates, int target) {
        Arrays.sort(candidates);
        Set<List<Integer>> rows = new HashSet<>();
        backtrack(candidates, 0, target, new ArrayList<>(), rows);
        return new ArrayList<>(rows);
    }

    private void backtrack(int[] candidates, int index, int remaining, List<Integer> path, Set<List<Integer>> rows) {
        if (remaining == 0) {
            rows.add(new ArrayList<>(path));
            return;
        }
        if (index == candidates.length || remaining < 0) return;
        path.add(candidates[index]);
        backtrack(candidates, index + 1, remaining - candidates[index], path, rows);
        path.remove(path.size() - 1);
        backtrack(candidates, index + 1, remaining, path, rows);
    }
}
