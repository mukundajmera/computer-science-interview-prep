package iterator.v2;

import java.util.ArrayDeque;
import java.util.ArrayList;
import java.util.Collections;
import java.util.Deque;
import java.util.Iterator;
import java.util.List;
import java.util.NoSuchElementException;

/**
 * v2-variant: Composite Tree Iterators (DFS Depth-First vs. BFS Breadth-First).
 * Demonstrates decoupling composite data structures from multiple simultaneous
 * traversal strategies using the Iterator pattern.
 */
public class TreeIteratorDemo {

    public static class TreeNode {
        private final String name;
        private final List<TreeNode> children = new ArrayList<>();

        public TreeNode(String name) {
            this.name = name;
        }

        public String getName() {
            return name;
        }

        public TreeNode addChild(TreeNode child) {
            this.children.add(child);
            return this;
        }

        public List<TreeNode> getChildren() {
            return Collections.unmodifiableList(children);
        }

        public Iterator<TreeNode> dfsIterator() {
            return new DfsIterator(this);
        }

        public Iterator<TreeNode> bfsIterator() {
            return new BfsIterator(this);
        }
    }

    public static class DfsIterator implements Iterator<TreeNode> {
        private final Deque<TreeNode> stack = new ArrayDeque<>();

        public DfsIterator(TreeNode root) {
            if (root != null) {
                stack.push(root);
            }
        }

        @Override
        public boolean hasNext() {
            return !stack.isEmpty();
        }

        @Override
        public TreeNode next() {
            if (!hasNext()) {
                throw new NoSuchElementException();
            }
            TreeNode current = stack.pop();
            // Push children in reverse order so leftmost child is visited first
            List<TreeNode> children = current.getChildren();
            for (int i = children.size() - 1; i >= 0; i--) {
                stack.push(children.get(i));
            }
            return current;
        }
    }

    public static class BfsIterator implements Iterator<TreeNode> {
        private final Deque<TreeNode> queue = new ArrayDeque<>();

        public BfsIterator(TreeNode root) {
            if (root != null) {
                queue.offer(root);
            }
        }

        @Override
        public boolean hasNext() {
            return !queue.isEmpty();
        }

        @Override
        public TreeNode next() {
            if (!hasNext()) {
                throw new NoSuchElementException();
            }
            TreeNode current = queue.poll();
            for (TreeNode child : current.getChildren()) {
                queue.offer(child);
            }
            return current;
        }
    }

    public static void main(String[] args) {
        TreeNode root = new TreeNode("CEO");
        TreeNode vpEng = new TreeNode("VP_ENG");
        TreeNode vpSales = new TreeNode("VP_SALES");
        root.addChild(vpEng).addChild(vpSales);
        vpEng.addChild(new TreeNode("ENG_LEAD_1")).addChild(new TreeNode("ENG_LEAD_2"));

        System.out.println("DFS Traversal:");
        Iterator<TreeNode> dfs = root.dfsIterator();
        while (dfs.hasNext()) {
            System.out.print(dfs.next().getName() + " -> ");
        }
        System.out.println("END");
    }
}
