import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;

class Solution {
    public List<List<Integer>> combinationSum(int[] candidates, int target) {
        Arrays.sort(candidates);
        List<List<Integer>> result = new ArrayList<>();
        backtrack(candidates, target, 0, new ArrayList<>(), result);
        return result;
    }

    private void backtrack(int[] candidates, int remaining, int start, List<Integer> path, List<List<Integer>> result) {
        if (remaining == 0) {
            result.add(new ArrayList<>(path));
            return;
        }
        if (start == candidates.length || remaining < candidates[start]) {
            return;
        }
        path.add(candidates[start]);
        backtrack(candidates, remaining - candidates[start], start, path, result);
        path.remove(path.size() - 1);
        backtrack(candidates, remaining, start + 1, path, result);
    }
}
