
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.concurrent.CountDownLatch;

public class SubscriberDAG {
    private final Map<String, List<String>> dependencies;
    private final Map<String, Runnable> tasks;

    public SubscriberDAG() {
        this.dependencies = new HashMap<>();
        this.tasks = new HashMap<>();
    }

    public void addSubscriber(String subscriberId, Runnable task) {
        tasks.put(subscriberId, task);
        dependencies.putIfAbsent(subscriberId, new ArrayList<>());
    }

    public void addDependency(String from, String to) {
        dependencies.putIfAbsent(from, new ArrayList<>());
        dependencies.get(from).add(to);
    }

    public void execute() throws InterruptedException {
        // Simple implementation: Topological sort and execute sequentially,
        // or execute in parallel using CountDownLatches for dependencies.
        // Let's do sequential topological sort for simplicity.
        
        Map<String, Integer> inDegree = new HashMap<>();
        for (String node : tasks.keySet()) {
            inDegree.put(node, 0);
        }

        for (List<String> deps : dependencies.values()) {
            for (String dep : deps) {
                inDegree.put(dep, inDegree.getOrDefault(dep, 0) + 1);
            }
        }

        List<String> queue = new ArrayList<>();
        for (Map.Entry<String, Integer> entry : inDegree.entrySet()) {
            if (entry.getValue() == 0) {
                queue.add(entry.getKey());
            }
        }

        List<String> order = new ArrayList<>();
        while (!queue.isEmpty()) {
            String current = queue.remove(0);
            order.add(current);

            List<String> currentDeps = dependencies.getOrDefault(current, new ArrayList<>());
            for (String neighbor : currentDeps) {
                inDegree.put(neighbor, inDegree.get(neighbor) - 1);
                if (inDegree.get(neighbor) == 0) {
                    queue.add(neighbor);
                }
            }
        }

        if (order.size() != tasks.size()) {
            throw new IllegalStateException("Cycle detected in subscriber DAG");
        }

        for (String sub : order) {
            tasks.get(sub).run();
        }
    }
}
