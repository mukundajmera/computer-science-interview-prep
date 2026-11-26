import java.util.*;

public class SolutionsTest {
    
    private static Solutions.TreeNode buildTree(Integer[] values) {
        if (values == null || values.length == 0) return null;
        Solutions.TreeNode root = new Solutions.TreeNode(values[0]);
        Queue<Solutions.TreeNode> queue = new LinkedList<>();
        queue.offer(root);
        int i = 1;
        while (i < values.length) {
            Solutions.TreeNode curr = queue.poll();
            if (values[i] != null) {
                curr.left = new Solutions.TreeNode(values[i]);
                queue.offer(curr.left);
            }
            i++;
            if (i < values.length && values[i] != null) {
                curr.right = new Solutions.TreeNode(values[i]);
                queue.offer(curr.right);
            }
            i++;
        }
        return root;
    }

    public static void main(String[] args) {
        Solutions sol = new Solutions();

        // 1. levelOrder
        assert sol.levelOrder(buildTree(new Integer[]{3,9,20,null,null,15,7})).equals(Arrays.asList(Arrays.asList(3), Arrays.asList(9,20), Arrays.asList(15,7)));
        assert sol.levelOrder(buildTree(new Integer[]{1})).equals(Arrays.asList(Arrays.asList(1)));
        assert sol.levelOrder(buildTree(new Integer[]{})).equals(Arrays.asList());
        assert sol.levelOrder(buildTree(new Integer[]{1,2,3,4,5,6,7})).equals(Arrays.asList(Arrays.asList(1), Arrays.asList(2,3), Arrays.asList(4,5,6,7)));
        assert sol.levelOrder(buildTree(new Integer[]{1,null,2,null,3})).equals(Arrays.asList(Arrays.asList(1), Arrays.asList(2), Arrays.asList(3)));
        assert sol.levelOrder(buildTree(new Integer[]{1,2,null,3,null,4,null})).equals(Arrays.asList(Arrays.asList(1), Arrays.asList(2), Arrays.asList(3), Arrays.asList(4)));

        // 2. minDepth
        assert sol.minDepth(buildTree(new Integer[]{3,9,20,null,null,15,7})) == 2;
        assert sol.minDepth(buildTree(new Integer[]{2,null,3,null,4,null,5,null,6})) == 5;
        assert sol.minDepth(buildTree(new Integer[]{})) == 0;
        assert sol.minDepth(buildTree(new Integer[]{1})) == 1;
        assert sol.minDepth(buildTree(new Integer[]{1,2,3})) == 2;
        assert sol.minDepth(buildTree(new Integer[]{1,2,3,4,null,null,5})) == 3;

        // 3. rightSideView
        assert sol.rightSideView(buildTree(new Integer[]{1,2,3,null,5,null,4})).equals(Arrays.asList(1,3,4));
        assert sol.rightSideView(buildTree(new Integer[]{1,null,3})).equals(Arrays.asList(1,3));
        assert sol.rightSideView(buildTree(new Integer[]{})).equals(Arrays.asList());
        assert sol.rightSideView(buildTree(new Integer[]{1,2,3,4})).equals(Arrays.asList(1,3,4));
        assert sol.rightSideView(buildTree(new Integer[]{1,2})).equals(Arrays.asList(1,2));
        assert sol.rightSideView(buildTree(new Integer[]{1,2,3,4,5,6,7})).equals(Arrays.asList(1,3,7));

        // 4. numIslands
        assert sol.numIslands(new char[][]{{'1','1','1','1','0'},{'1','1','0','1','0'},{'1','1','0','0','0'},{'0','0','0','0','0'}}) == 1;
        assert sol.numIslands(new char[][]{{'1','1','0','0','0'},{'1','1','0','0','0'},{'0','0','1','0','0'},{'0','0','0','1','1'}}) == 3;
        assert sol.numIslands(new char[][]{{'0'}}) == 0;
        assert sol.numIslands(new char[][]{{'1'}}) == 1;
        assert sol.numIslands(new char[][]{{'1','0','1'},{'0','1','0'},{'1','0','1'}}) == 5;
        assert sol.numIslands(new char[][]{{'1','1'},{'1','1'}}) == 1;

        // 5. orangesRotting
        assert sol.orangesRotting(new int[][]{{2,1,1},{1,1,0},{0,1,1}}) == 4;
        assert sol.orangesRotting(new int[][]{{2,1,1},{0,1,1},{1,0,1}}) == -1;
        assert sol.orangesRotting(new int[][]{{0,2}}) == 0;
        assert sol.orangesRotting(new int[][]{{0}}) == 0;
        assert sol.orangesRotting(new int[][]{{1}}) == -1;
        assert sol.orangesRotting(new int[][]{{2,2},{1,1},{0,0},{2,0}}) == 1;

        // 6. shortestPathBinaryMatrix
        assert sol.shortestPathBinaryMatrix(new int[][]{{0,1},{1,0}}) == 2;
        assert sol.shortestPathBinaryMatrix(new int[][]{{0,0,0},{1,1,0},{1,1,0}}) == 4;
        assert sol.shortestPathBinaryMatrix(new int[][]{{1,0,0},{1,1,0},{1,1,0}}) == -1;
        assert sol.shortestPathBinaryMatrix(new int[][]{{0}}) == 1;
        assert sol.shortestPathBinaryMatrix(new int[][]{{1}}) == -1;
        assert sol.shortestPathBinaryMatrix(new int[][]{{0,0,0},{0,0,0},{0,0,0}}) == 3;

        // 7. ladderLength
        assert sol.ladderLength("hit", "cog", Arrays.asList("hot","dot","dog","lot","log","cog")) == 5;
        assert sol.ladderLength("hit", "cog", Arrays.asList("hot","dot","dog","lot","log")) == 0;
        assert sol.ladderLength("a", "c", Arrays.asList("a","b","c")) == 2;
        assert sol.ladderLength("a", "b", Arrays.asList("c")) == 0;
        assert sol.ladderLength("a", "b", Arrays.asList("b")) == 2;
        assert sol.ladderLength("qa", "sq", Arrays.asList("si","go","se","cm","so","ph","mt","db","mb","sb","kr","ln","tm","le","av","sm","ar","ci","ca","br","ti","ba","to","ra","fa","yo","ow","sn","ya","cr","po","fe","ho","ma","re","or","rn","au","ur","rh","sr","tc","lt","lo","as","fr","nb","yb","if","pb","ge","th","pm","rb","sh","co","ga","li","ha","hz","no","bi","di","hi","qa","pi","os","uh","wm","an","me","mo","na","la","st","er","sc","ne","mn","mi","am","ex","pt","io","be","fm","ta","tb","ni","mr","pa","he","lr","sq","ye")) == 5;

        // 8. canFinish
        assert sol.canFinish(2, new int[][]{{1,0}}) == true;
        assert sol.canFinish(2, new int[][]{{1,0},{0,1}}) == false;
        assert sol.canFinish(1, new int[][]{}) == true;
        assert sol.canFinish(3, new int[][]{{0,1},{1,2},{2,0}}) == false;
        assert sol.canFinish(3, new int[][]{{0,1},{0,2},{1,2}}) == true;
        assert sol.canFinish(4, new int[][]{{1,0},{2,0},{3,1},{3,2}}) == true;

        System.out.println("All Java tests passed.");
    }
}
