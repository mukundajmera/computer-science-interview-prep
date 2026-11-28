package v2_extended;

import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.CopyOnWriteArrayList;

public class Mailbox {
    private final String userId;
    private final Map<String, List<EmailMessage>> folders;
    private final Map<String, String> messageFolderMapping;

    public Mailbox(String userId) {
        this.userId = userId;
        this.folders = new ConcurrentHashMap<>();
        this.folders.put("Inbox", new CopyOnWriteArrayList<>());
        this.folders.put("Sent", new CopyOnWriteArrayList<>());
        this.folders.put("Drafts", new CopyOnWriteArrayList<>());
        this.folders.put("Trash", new CopyOnWriteArrayList<>());
        this.folders.put("Spam", new CopyOnWriteArrayList<>());
        this.messageFolderMapping = new ConcurrentHashMap<>();
    }

    public String getUserId() {
        return userId;
    }

    public void addMessage(String folderName, EmailMessage message) {
        folders.computeIfAbsent(folderName, k -> new CopyOnWriteArrayList<>()).add(message);
        messageFolderMapping.put(message.getMessageId(), folderName);
    }

    public boolean moveMessage(String messageId, String targetFolder) {
        String currentFolder = messageFolderMapping.get(messageId);
        if (currentFolder == null || currentFolder.equals(targetFolder)) {
            return false;
        }
        
        List<EmailMessage> sourceList = folders.get(currentFolder);
        if (sourceList != null) {
            EmailMessage msgToMove = null;
            // Since we use CopyOnWriteArrayList, iteration is safe
            for (EmailMessage msg : sourceList) {
                if (msg.getMessageId().equals(messageId)) {
                    msgToMove = msg;
                    break;
                }
            }
            if (msgToMove != null) {
                sourceList.remove(msgToMove);
                folders.computeIfAbsent(targetFolder, k -> new CopyOnWriteArrayList<>()).add(msgToMove);
                messageFolderMapping.put(messageId, targetFolder);
                return true;
            }
        }
        return false;
    }

    public List<EmailMessage> getMessagesInFolder(String folderName) {
        return folders.getOrDefault(folderName, Collections.emptyList());
    }
    
    public int getUnreadCount(String folderName) {
        return (int) getMessagesInFolder(folderName).stream()
                .filter(msg -> !msg.isRead())
                .count();
    }
    
    public EmailMessage getMessageById(String messageId) {
        String folder = messageFolderMapping.get(messageId);
        if (folder != null) {
            return folders.get(folder).stream()
                    .filter(msg -> msg.getMessageId().equals(messageId))
                    .findFirst()
                    .orElse(null);
        }
        return null;
    }

    public void deleteMessage(String messageId) {
        moveMessage(messageId, "Trash");
    }
}
