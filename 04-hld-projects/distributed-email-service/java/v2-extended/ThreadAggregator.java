package v2_extended;

/**
 * v2-extended thread aggregator.
 *
 * Improvement over v1-basic (named per the repo rule v1-basic -> v2-extended):
 * 3. Order-independent conversation threading (PITFALLS #5, brittle
 *    threading): v1 grouped a reply into its parent's thread only if the
 *    parent appeared EARLIER in the input list, so a reply delivered before
 *    its parent (normal for external mail) started a phantom thread. v2
 *    indexes messages by Message-ID first, then walks each message's
 *    In-Reply-To / References chain up to the thread root regardless of
 *    arrival order, with a deterministic cycle guard for malformed headers,
 *    and returns each thread sorted by timestamp.
 */

import java.util.ArrayList;
import java.util.Comparator;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;

public class ThreadAggregator {
    public static List<List<EmailMessage>> groupMessagesIntoThreads(List<EmailMessage> messages) {
        Map<String, EmailMessage> byId = new HashMap<>();
        for (EmailMessage msg : messages) {
            byId.put(msg.getMessageId(), msg);
        }

        Map<String, List<EmailMessage>> threadMap = new HashMap<>();
        for (EmailMessage msg : messages) {
            String rootId = findRoot(msg, byId);
            threadMap.computeIfAbsent(rootId, k -> new ArrayList<>()).add(msg);
        }

        List<List<EmailMessage>> threads = new ArrayList<>(threadMap.values());
        for (List<EmailMessage> thread : threads) {
            thread.sort(Comparator.comparing(EmailMessage::getTimestamp));
        }
        return threads;
    }

    private static String findRoot(EmailMessage msg, Map<String, EmailMessage> byId) {
        Set<String> seen = new HashSet<>();
        EmailMessage current = msg;
        while (!seen.contains(current.getMessageId())) {
            seen.add(current.getMessageId());
            EmailMessage parent = null;
            if (current.getInReplyTo() != null && byId.containsKey(current.getInReplyTo())) {
                parent = byId.get(current.getInReplyTo());
            } else if (current.getReferences() != null) {
                for (String ref : current.getReferences()) {
                    if (byId.containsKey(ref)) {
                        parent = byId.get(ref);
                        break;
                    }
                }
            }
            if (parent == null) {
                return current.getMessageId();
            }
            current = parent;
        }
        // Cycle in the headers: anchor the whole cycle at one shared,
        // deterministic id so every member lands in the same thread.
        String anchor = null;
        for (String id : seen) {
            if (anchor == null || id.compareTo(anchor) < 0) {
                anchor = id;
            }
        }
        return anchor;
    }
}
