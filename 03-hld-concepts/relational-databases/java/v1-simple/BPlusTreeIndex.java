package v1_simple;

import java.util.ArrayList;
import java.util.Collections;
import java.util.List;

public class BPlusTreeIndex<K extends Comparable<K>, V> {
    private int order;
    private Node root;

    public BPlusTreeIndex(int order) {
        this.order = Math.max(3, order);
        this.root = new LeafNode();
    }

    abstract class Node {
        boolean isLeaf;
        List<K> keys;

        Node(boolean isLeaf) {
            this.isLeaf = isLeaf;
            this.keys = new ArrayList<>();
        }
    }

    class LeafNode extends Node {
        List<V> values;
        LeafNode nextLeaf;

        LeafNode() {
            super(true);
            this.values = new ArrayList<>();
            this.nextLeaf = null;
        }
    }

    class InternalNode extends Node {
        List<Node> children;

        InternalNode() {
            super(false);
            this.children = new ArrayList<>();
        }
    }

    public void insert(K key, V value) {
        if (root.keys.size() == order - 1) {
            InternalNode newRoot = new InternalNode();
            newRoot.children.add(root);
            splitChild(newRoot, 0);
            root = newRoot;
            insertNonFull(newRoot, key, value);
        } else {
            insertNonFull(root, key, value);
        }
    }

    private void splitChild(InternalNode parent, int index) {
        Node child = parent.children.get(index);
        if (child.isLeaf) {
            splitLeaf(parent, index, (LeafNode) child);
        } else {
            splitInternal(parent, index, (InternalNode) child);
        }
    }

    private void splitLeaf(InternalNode parent, int index, LeafNode leaf) {
        LeafNode newLeaf = new LeafNode();
        int mid = order / 2;

        newLeaf.keys.addAll(leaf.keys.subList(mid, leaf.keys.size()));
        newLeaf.values.addAll(leaf.values.subList(mid, leaf.values.size()));

        leaf.keys.subList(mid, leaf.keys.size()).clear();
        leaf.values.subList(mid, leaf.values.size()).clear();

        newLeaf.nextLeaf = leaf.nextLeaf;
        leaf.nextLeaf = newLeaf;

        parent.children.add(index + 1, newLeaf);
        parent.keys.add(index, newLeaf.keys.get(0));
    }

    private void splitInternal(InternalNode parent, int index, InternalNode internal) {
        InternalNode newInternal = new InternalNode();
        int mid = order / 2;

        K upKey = internal.keys.get(mid);

        newInternal.keys.addAll(internal.keys.subList(mid + 1, internal.keys.size()));
        newInternal.children.addAll(internal.children.subList(mid + 1, internal.children.size()));

        internal.keys.subList(mid, internal.keys.size()).clear();
        internal.children.subList(mid + 1, internal.children.size()).clear();

        parent.children.add(index + 1, newInternal);
        parent.keys.add(index, upKey);
    }

    private void insertNonFull(Node node, K key, V value) {
        if (node.isLeaf) {
            LeafNode leaf = (LeafNode) node;
            int idx = Collections.binarySearch(leaf.keys, key);
            if (idx >= 0) {
                leaf.values.set(idx, value);
            } else {
                idx = -(idx + 1);
                leaf.keys.add(idx, key);
                leaf.values.add(idx, value);
            }
        } else {
            InternalNode internal = (InternalNode) node;
            int idx = Collections.binarySearch(internal.keys, key);
            if (idx < 0) {
                idx = -(idx + 1);
            } else {
                idx++;
            }
            Node child = internal.children.get(idx);
            if (child.keys.size() == order - 1) {
                splitChild(internal, idx);
                if (key.compareTo(internal.keys.get(idx)) >= 0) {
                    idx++;
                }
            }
            insertNonFull(internal.children.get(idx), key, value);
        }
    }

    public V search(K key) {
        LeafNode leaf = findLeaf(root, key);
        int idx = Collections.binarySearch(leaf.keys, key);
        if (idx >= 0) {
            return leaf.values.get(idx);
        }
        return null;
    }

    public List<Entry<K, V>> rangeScan(K startKey, K endKey) {
        LeafNode leaf = findLeaf(root, startKey);
        List<Entry<K, V>> results = new ArrayList<>();
        while (leaf != null) {
            for (int i = 0; i < leaf.keys.size(); i++) {
                K k = leaf.keys.get(i);
                if (k.compareTo(startKey) >= 0 && k.compareTo(endKey) <= 0) {
                    results.add(new Entry<>(k, leaf.values.get(i)));
                } else if (k.compareTo(endKey) > 0) {
                    return results;
                }
            }
            leaf = leaf.nextLeaf;
        }
        return results;
    }

    private LeafNode findLeaf(Node node, K key) {
        while (!node.isLeaf) {
            InternalNode internal = (InternalNode) node;
            int idx = Collections.binarySearch(internal.keys, key);
            if (idx < 0) {
                idx = -(idx + 1);
            } else {
                idx++;
            }
            node = internal.children.get(idx);
        }
        return (LeafNode) node;
    }

    public static class Entry<K, V> {
        public final K key;
        public final V value;

        public Entry(K key, V value) {
            this.key = key;
            this.value = value;
        }

        @Override
        public boolean equals(Object obj) {
            if (this == obj) return true;
            if (!(obj instanceof Entry)) return false;
            Entry<?, ?> other = (Entry<?, ?>) obj;
            return key.equals(other.key) && value.equals(other.value);
        }

        @Override
        public String toString() {
            return "Entry{" + key + "=" + value + "}";
        }
    }
}
