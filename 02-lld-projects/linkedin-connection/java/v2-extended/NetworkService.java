package v2_extended;

import java.util.*;

/**
 * LinkedIn Connection System - V1 Basic
 * 
 * NetworkService class - Facade for connection operations.
 * Implements Singleton pattern.
 */
class NetworkService {
    private static NetworkService instance;
    
    private final Map<String, User> users;
    private final Map<String, ConnectionRequest> pendingRequests;

    private NetworkService() {
        this.users = new HashMap<>();
        this.pendingRequests = new HashMap<>();
    }

    public static synchronized NetworkService getInstance() {
        if (instance == null) {
            instance = new NetworkService();
        }
        return instance;
    }

    public static synchronized void resetInstance() {
        instance = null;
    }

    /**
     * Register a new user.
     */
    public boolean registerUser(User user) {
        if (user == null || users.containsKey(user.getUserId())) {
            return false;
        }
        users.put(user.getUserId(), user);
        return true;
    }

    /**
     * Get user by ID.
     */
    public User getUser(String userId) {
        return users.get(userId);
    }

    /**
     * Get all registered users.
     */
    public List<User> getAllUsers() {
        return new ArrayList<>(users.values());
    }

    /**
     * Send a connection request.
     */
    public ConnectionRequest sendConnectionRequest(String senderId, String receiverId) {
        return sendConnectionRequest(senderId, receiverId, null);
    }

    public ConnectionRequest sendConnectionRequest(String senderId, String receiverId, String message) {
        User sender = users.get(senderId);
        User receiver = users.get(receiverId);
        
        if (sender == null || receiver == null) {
            System.out.println("User not found");
            return null;
        }
        
        if (sender.equals(receiver)) {
            System.out.println("Cannot send connection request to yourself");
            return null;
        }
        
        if (sender.isConnectedTo(receiver)) {
            System.out.println("Already connected");
            return null;
        }
        
        // Check for existing pending request
        for (ConnectionRequest request : sender.getSentRequests()) {
            if (request.getReceiver().equals(receiver) && request.isPending()) {
                System.out.println("Pending request already exists");
                return null;
            }
        }
        
        ConnectionRequest request = new ConnectionRequest(sender, receiver, message);
        sender.addSentRequest(request);
        receiver.addReceivedRequest(request);
        pendingRequests.put(request.getRequestId(), request);
        
        System.out.println(sender.getName() + " sent connection request to " + receiver.getName());
        return request;
    }

    /**
     * Accept a connection request.
     */
    public boolean acceptRequest(String requestId) {
        ConnectionRequest request = pendingRequests.get(requestId);
        if (request == null) {
            System.out.println("Request not found");
            return false;
        }
        
        if (request.accept()) {
            pendingRequests.remove(requestId);
            System.out.println(request.getReceiver().getName() + " accepted " + 
                             request.getSender().getName() + "'s connection request");
            return true;
        }
        return false;
    }

    /**
     * Reject a connection request.
     */
    public boolean rejectRequest(String requestId) {
        ConnectionRequest request = pendingRequests.get(requestId);
        if (request == null) {
            System.out.println("Request not found");
            return false;
        }
        
        if (request.reject()) {
            pendingRequests.remove(requestId);
            System.out.println(request.getReceiver().getName() + " rejected " + 
                             request.getSender().getName() + "'s connection request");
            return true;
        }
        return false;
    }

    /**
     * Withdraw a connection request.
     */
    public boolean withdrawRequest(String requestId) {
        ConnectionRequest request = pendingRequests.get(requestId);
        if (request == null) {
            return false;
        }
        
        if (request.withdraw()) {
            pendingRequests.remove(requestId);
            return true;
        }
        return false;
    }

    /**
     * Remove a connection between two users.
     */
    public boolean removeConnection(String userId1, String userId2) {
        User user1 = users.get(userId1);
        User user2 = users.get(userId2);
        
        if (user1 == null || user2 == null) {
            return false;
        }
        
        user1.removeConnection(user2);
        user2.removeConnection(user1);
        return true;
    }

    /**
     * Get connections of a user.
     */
    public Set<User> getConnections(String userId) {
        User user = users.get(userId);
        if (user == null) {
            return Collections.emptySet();
        }
        return user.getConnections();
    }

    /**
     * Get mutual connections between two users.
     */
    public Set<User> getMutualConnections(String userId1, String userId2) {
        User user1 = users.get(userId1);
        User user2 = users.get(userId2);
        
        if (user1 == null || user2 == null) {
            return Collections.emptySet();
        }
        
        return user1.getMutualConnections(user2);
    }

    /**
     * Get pending requests for a user.
     */
    public List<ConnectionRequest> getPendingRequests(String userId) {
        User user = users.get(userId);
        if (user == null) {
            return Collections.emptyList();
        }
        return user.getPendingReceivedRequests();
    }

    /**
     * Check if two users are connected.
     */
    public boolean areConnected(String userId1, String userId2) {
        User user1 = users.get(userId1);
        User user2 = users.get(userId2);
        
        if (user1 == null || user2 == null) {
            return false;
        }
        
        return user1.isConnectedTo(user2);
    }

    /**
     * Get user count.
     */
    public int getUserCount() {
        return users.size();
    }

    /**
     * Get total connection count.
     */
    public int getTotalConnectionCount() {
        int total = 0;
        for (User user : users.values()) {
            total += user.getConnectionCount();
        }
        return total / 2; // Divide by 2 since connections are bidirectional
    }

    /**
     * Get connection degree between two users using BFS.
     */
    public int getConnectionDegree(String userId1, String userId2) {
        if (userId1.equals(userId2)) return 0;
        User user1 = users.get(userId1);
        User user2 = users.get(userId2);
        if (user1 == null || user2 == null) return -1;
        
        Queue<User> queue = new LinkedList<>();
        Set<User> visited = new HashSet<>();
        queue.add(user1);
        visited.add(user1);
        
        int degree = 0;
        while (!queue.isEmpty()) {
            int size = queue.size();
            degree++;
            for (int i = 0; i < size; i++) {
                User curr = queue.poll();
                if (curr.getConnections().contains(user2)) {
                    return degree;
                }
                for (User connection : curr.getConnections()) {
                    if (!visited.contains(connection)) {
                        visited.add(connection);
                        queue.add(connection);
                    }
                }
            }
        }
        return -1;
    }

    /**
     * Endorse a skill of a connection.
     */
    public boolean endorseSkill(String endorserId, String endorseeId, String skillName) {
        if (!areConnected(endorserId, endorseeId)) {
            return false;
        }
        
        User endorser = users.get(endorserId);
        User endorsee = users.get(endorseeId);
        
        if (endorser == null || endorsee == null) {
            return false;
        }
        
        // This assumes User has getSkill(skillName) method and Skill has addEndorsement(User)
        // Check if the Skill class and methods exist
        Skill skill = endorsee.getSkill(skillName);
        if (skill != null) {
            skill.addEndorsement(endorser);
            return true;
        }
        return false;
    }
}
