package v1_basic;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;

public class ThreadAggregator {
    public static List<List<EmailMessage>> groupMessagesIntoThreads(List<EmailMessage> messages) {
        Map<String, List<EmailMessage>> threadMap = new ConcurrentHashMap<>();
        Map<String, String> messageToThreadMap = new ConcurrentHashMap<>();

        for (EmailMessage msg : messages) {
            String messageId = msg.getMessageId();
            String inReplyTo = msg.getInReplyTo();
            
            String threadId = null;
            if (inReplyTo != null && messageToThreadMap.containsKey(inReplyTo)) {
                threadId = messageToThreadMap.get(inReplyTo);
            } else if (msg.getReferences() != null && !msg.getReferences().isEmpty()) {
                for (String ref : msg.getReferences()) {
                    if (messageToThreadMap.containsKey(ref)) {
                        threadId = messageToThreadMap.get(ref);
                        break;
                    }
                }
            }

            if (threadId == null) {
                threadId = messageId;
            }

            messageToThreadMap.put(messageId, threadId);
            threadMap.computeIfAbsent(threadId, k -> new ArrayList<>()).add(msg);
        }

        return new ArrayList<>(threadMap.values());
    }
}
