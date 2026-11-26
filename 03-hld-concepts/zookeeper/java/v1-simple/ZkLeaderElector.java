package v1_simple;

import java.util.*;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.locks.ReentrantLock;
import java.util.function.Consumer;

public class ZkLeaderElector {

    public static class ZNode {
        public final String name;
        public final String data;
        public final boolean ephemeral;
        public final String sessionId;

        public ZNode(String name, String data, boolean ephemeral, String sessionId) {
            this.name = name;
            this.data = data;
            this.ephemeral = ephemeral;
            this.sessionId = sessionId;
        }
    }

    public static class ZkSimulator {
        private final Map<String, ZNode> nodes = new ConcurrentHashMap<>();
        private final Map<String, List<Consumer<String>>> watches = new ConcurrentHashMap<>();
        private int sequenceNumber = 0;
        private final ReentrantLock lock = new ReentrantLock();

        public String create(String path, String data, boolean ephemeral, boolean sequential, String sessionId) {
            lock.lock();
            try {
                String finalPath = path;
                if (sequential) {
                    finalPath = String.format("%s%010d", path, sequenceNumber++);
                }

                if (nodes.containsKey(finalPath)) {
                    throw new IllegalArgumentException("Node already exists");
                }

                nodes.put(finalPath, new ZNode(finalPath, data, ephemeral, sessionId));
                return finalPath;
            } finally {
                lock.unlock();
            }
        }

        public List<String> getChildren(String parentPath) {
            lock.lock();
            try {
                String prefix = parentPath.endsWith("/") ? parentPath : parentPath + "/";
                List<String> children = new ArrayList<>();
                for (String path : nodes.keySet()) {
                    if (path.startsWith(prefix)) {
                        String suffix = path.substring(prefix.length());
                        if (!suffix.contains("/")) {
                            children.add(suffix);
                        }
                    }
                }
                return children;
            } finally {
                lock.unlock();
            }
        }

        public boolean exists(String path, Consumer<String> watch) {
            lock.lock();
            try {
                boolean exists = nodes.containsKey(path);
                if (watch != null) {
                    watches.computeIfAbsent(path, k -> new ArrayList<>()).add(watch);
                }
                return exists;
            } finally {
                lock.unlock();
            }
        }

        public void delete(String path) {
            boolean deleted = false;
            lock.lock();
            try {
                if (nodes.containsKey(path)) {
                    nodes.remove(path);
                    deleted = true;
                }
            } finally {
                lock.unlock();
            }
            if (deleted) {
                triggerWatches(path);
            }
        }

        private void triggerWatches(String path) {
            List<Consumer<String>> callbacks;
            lock.lock();
            try {
                callbacks = watches.remove(path); // watches are one-shot
            } finally {
                lock.unlock();
            }

            if (callbacks != null) {
                for (Consumer<String> cb : callbacks) {
                    cb.accept(path);
                }
            }
        }

        public void expireSession(String sessionId) {
            List<String> pathsToDelete = new ArrayList<>();
            lock.lock();
            try {
                for (Map.Entry<String, ZNode> entry : nodes.entrySet()) {
                    if (entry.getValue().ephemeral && sessionId.equals(entry.getValue().sessionId)) {
                        pathsToDelete.add(entry.getKey());
                    }
                }
                for (String path : pathsToDelete) {
                    nodes.remove(path);
                }
            } finally {
                lock.unlock();
            }

            // Trigger watches without lock to prevent deadlock
            for (String path : pathsToDelete) {
                triggerWatches(path);
            }
        }

        // Expose watch count for testing
        public int getWatchCount(String path) {
            lock.lock();
            try {
                List<Consumer<String>> callbacks = watches.get(path);
                return callbacks != null ? callbacks.size() : 0;
            } finally {
                lock.unlock();
            }
        }
    }

    private final ZkSimulator zk;
    private final String electionPath;
    private final String sessionId;
    private String nodePath;
    private boolean isLeader;
    private Consumer<Boolean> onLeadershipChange;

    public ZkLeaderElector(ZkSimulator zk, String electionPath, String sessionId) {
        this.zk = zk;
        this.electionPath = electionPath;
        this.sessionId = sessionId;
        this.isLeader = false;

        if (!this.zk.exists(this.electionPath, null)) {
            try {
                this.zk.create(this.electionPath, "election_parent", false, false, null);
            } catch (IllegalArgumentException e) {
                // Already created
            }
        }
    }

    public void setOnLeadershipChange(Consumer<Boolean> onLeadershipChange) {
        this.onLeadershipChange = onLeadershipChange;
    }

    public void joinElection() {
        String prefix = this.electionPath + "/n_";
        this.nodePath = this.zk.create(prefix, this.sessionId, true, true, this.sessionId);
        checkLeadership();
    }

    public boolean isLeader() {
        return this.isLeader;
    }

    public String getNodePath() {
        return this.nodePath;
    }

    private void checkLeadership() {
        List<String> children = this.zk.getChildren(this.electionPath);
        Collections.sort(children);

        String[] pathParts = this.nodePath.split("/");
        String myNodeName = pathParts[pathParts.length - 1];

        if (children.isEmpty()) {
            return;
        }

        if (myNodeName.equals(children.get(0))) {
            this.isLeader = true;
            if (this.onLeadershipChange != null) {
                this.onLeadershipChange.accept(true);
            }
        } else {
            this.isLeader = false;
            if (this.onLeadershipChange != null) {
                this.onLeadershipChange.accept(false);
            }

            int myIndex = children.indexOf(myNodeName);
            String precedingNodeName = children.get(myIndex - 1);
            String precedingPath = this.electionPath + "/" + precedingNodeName;

            boolean exists = this.zk.exists(precedingPath, this::onPrecedingNodeDeleted);
            if (!exists) {
                checkLeadership();
            }
        }
    }

    private void onPrecedingNodeDeleted(String path) {
        checkLeadership();
    }
}
