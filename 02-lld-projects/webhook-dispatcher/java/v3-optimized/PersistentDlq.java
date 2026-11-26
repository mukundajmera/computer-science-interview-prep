
import java.util.ArrayList;
import java.util.List;

public class PersistentDlq {
    private final int retentionDays;
    private final List<DlqItem> items = new ArrayList<>();

    public PersistentDlq(int retentionDays) {
        this.retentionDays = retentionDays;
    }

    public synchronized void add(WebhookTask task) {
        items.add(new DlqItem(task, System.currentTimeMillis()));
    }

    public synchronized List<WebhookTask> getItems() {
        List<WebhookTask> tasks = new ArrayList<>();
        for (DlqItem item : items) {
            tasks.add(item.task);
        }
        return tasks;
    }
    
    public synchronized void clear() {
        items.clear();
    }
    
    public int getRetentionDays() {
        return retentionDays;
    }

    private static class DlqItem {
        final WebhookTask task;
        final long timestamp;
        DlqItem(WebhookTask task, long timestamp) {
            this.task = task;
            this.timestamp = timestamp;
        }
    }
}
