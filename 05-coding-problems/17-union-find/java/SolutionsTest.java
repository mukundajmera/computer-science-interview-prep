import java.util.*;

public class SolutionsTest {
    public static void main(String[] args) {
        Solutions sol = new Solutions();
        
        // test findCircleNum
        assert sol.findCircleNum(new int[][]{{1,1,0},{1,1,0},{0,0,1}}) == 2;
        assert sol.findCircleNum(new int[][]{{1,0,0},{0,1,0},{0,0,1}}) == 3;
        assert sol.findCircleNum(new int[][]{{1}}) == 1;
        assert sol.findCircleNum(new int[][]{{1,1},{1,1}}) == 1;
        assert sol.findCircleNum(new int[][]{{1,0,1},{0,1,0},{1,0,1}}) == 2;
        assert sol.findCircleNum(new int[][]{{1,1,1},{1,1,1},{1,1,1}}) == 1;

        // test findRedundantConnection
        assert Arrays.equals(sol.findRedundantConnection(new int[][]{{1,2},{1,3},{2,3}}), new int[]{2,3});
        assert Arrays.equals(sol.findRedundantConnection(new int[][]{{1,2},{2,3},{3,4},{1,4},{1,5}}), new int[]{1,4});
        assert Arrays.equals(sol.findRedundantConnection(new int[][]{{1,2},{2,3},{1,3}}), new int[]{1,3});
        assert Arrays.equals(sol.findRedundantConnection(new int[][]{{1,2},{1,3},{3,4},{2,4}}), new int[]{2,4});
        assert Arrays.equals(sol.findRedundantConnection(new int[][]{{1,2},{1,3},{3,4},{4,5},{1,5}}), new int[]{1,5});
        assert Arrays.equals(sol.findRedundantConnection(new int[][]{{1,2},{2,3},{3,4},{4,5},{2,5}}), new int[]{2,5});

        // test countComponents
        assert sol.countComponents(5, new int[][]{{0,1},{1,2},{3,4}}) == 2;
        assert sol.countComponents(5, new int[][]{{0,1},{1,2},{2,3},{3,4}}) == 1;
        assert sol.countComponents(4, new int[][]{{0,1},{2,3}}) == 2;
        assert sol.countComponents(3, new int[][]{}) == 3;
        assert sol.countComponents(1, new int[][]{}) == 1;
        assert sol.countComponents(6, new int[][]{{0,1},{1,2},{2,3},{4,5}}) == 2;

        // test validTree
        assert sol.validTree(5, new int[][]{{0,1},{0,2},{0,3},{1,4}});
        assert !sol.validTree(5, new int[][]{{0,1},{1,2},{2,3},{1,3},{1,4}});
        assert !sol.validTree(4, new int[][]{{0,1},{2,3}});
        assert sol.validTree(1, new int[][]{});
        assert sol.validTree(3, new int[][]{{0,1},{0,2}});
        assert !sol.validTree(3, new int[][]{{0,1},{1,2},{0,2}});

        // test accountsMerge
        List<List<String>> accounts = Arrays.asList(
            Arrays.asList("John","a@m.com","b@m.com"),
            Arrays.asList("John","c@m.com"),
            Arrays.asList("John","a@m.com","d@m.com")
        );
        assert sol.accountsMerge(accounts).size() == 2;

        accounts = Arrays.asList(
            Arrays.asList("Gabe","g@m.com")
        );
        assert sol.accountsMerge(accounts).size() == 1;

        accounts = Arrays.asList(
            Arrays.asList("A","1@m.com"),
            Arrays.asList("A","2@m.com"),
            Arrays.asList("A","3@m.com")
        );
        assert sol.accountsMerge(accounts).size() == 3;

        accounts = Arrays.asList(
            Arrays.asList("A","1@m.com","2@m.com"),
            Arrays.asList("A","2@m.com","3@m.com")
        );
        assert sol.accountsMerge(accounts).size() == 1;
        
        accounts = Arrays.asList(
            Arrays.asList("A","1@m.com","2@m.com"),
            Arrays.asList("A","3@m.com","4@m.com"),
            Arrays.asList("A","2@m.com","4@m.com")
        );
        assert sol.accountsMerge(accounts).size() == 1;

        accounts = Arrays.asList(
            Arrays.asList("A","1@m.com"),
            Arrays.asList("B","2@m.com")
        );
        assert sol.accountsMerge(accounts).size() == 2;

        // test longestConsecutive
        assert sol.longestConsecutive(new int[]{100,4,200,1,3,2}) == 4;
        assert sol.longestConsecutive(new int[]{0,3,7,2,5,8,4,6,0,1}) == 9;
        assert sol.longestConsecutive(new int[]{}) == 0;
        assert sol.longestConsecutive(new int[]{1}) == 1;
        assert sol.longestConsecutive(new int[]{1,2,0,1}) == 3;
        assert sol.longestConsecutive(new int[]{9,1,4,7,3,-1,0,5,8,-1,6}) == 7;

        System.out.println("Java Tests Passed");
    }
}
