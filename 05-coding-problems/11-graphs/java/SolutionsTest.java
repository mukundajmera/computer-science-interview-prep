
import java.util.Arrays;

public class SolutionsTest {
    public static void main(String[] args) {
        Solutions sol = new Solutions();
        
        assert sol.canFinish(2, new int[][]{{1, 0}}) == true;
        assert sol.canFinish(2, new int[][]{{1, 0}, {0, 1}}) == false;
        
        assert Arrays.equals(sol.findOrder(2, new int[][]{{1, 0}}), new int[]{0, 1});
        assert Arrays.equals(sol.findOrder(2, new int[][]{{1, 0}, {0, 1}}), new int[]{});
        
        assert sol.validTree(5, new int[][]{{0, 1}, {0, 2}, {0, 3}, {1, 4}}) == true;
        assert sol.validTree(5, new int[][]{{0, 1}, {1, 2}, {2, 3}, {1, 3}, {1, 4}}) == false;
        
        assert sol.alienOrder(new String[]{"wrt", "wrf", "er", "ett", "rftt"}).equals("wertf");
        assert sol.alienOrder(new String[]{"z", "x"}).equals("zx");
        assert sol.alienOrder(new String[]{"z", "x", "z"}).equals("");
        
        assert sol.networkDelayTime(new int[][]{{2, 1, 1}, {2, 3, 1}, {3, 4, 1}}, 4, 2) == 2;
        assert sol.networkDelayTime(new int[][]{{1, 2, 1}}, 2, 1) == 1;
        assert sol.networkDelayTime(new int[][]{{1, 2, 1}}, 2, 2) == -1;
        
        assert sol.findCheapestPrice(3, new int[][]{{0, 1, 100}, {1, 2, 100}, {0, 2, 500}}, 0, 2, 1) == 200;
        assert sol.findCheapestPrice(3, new int[][]{{0, 1, 100}, {1, 2, 100}, {0, 2, 500}}, 0, 2, 0) == 500;
        
        assert sol.minCostConnectPoints(new int[][]{{0, 0}, {2, 2}, {3, 10}, {5, 2}, {7, 0}}) == 20;
        assert sol.minCostConnectPoints(new int[][]{{3, 12}, {-2, 5}, {-4, 1}}) == 18;
    }
}
