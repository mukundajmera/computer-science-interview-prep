package v3_optimized;

import java.util.*;
import java.time.LocalDateTime;

/**
 * LinkedIn Connection System - V1 Basic
 * 
 * User class representing a LinkedIn member.
 */
class User {
    private final String userId;
    private String name;
    private String email;
    private String headline;
    private String company;
    private final Set<User> connections;
    private final List<ConnectionRequest> sentRequests;
    private final List<ConnectionRequest> receivedRequests;
    private final Map<String, Skill> skills;

    public User(String userId, String name, String email) {
        if (userId == null || userId.isEmpty()) {
            throw new IllegalArgumentException("User ID cannot be null or empty");
        }
        this.userId = userId;
        this.name = name;
        this.email = email;
        this.headline = "";
        this.company = "";
        this.connections = new HashSet<>();
        this.sentRequests = new ArrayList<>();
        this.receivedRequests = new ArrayList<>();
        this.skills = new HashMap<>();
    }

    public User(String userId, String name, String email, String headline, String company) {
        this(userId, name, email);
        this.headline = headline != null ? headline : "";
        this.company = company != null ? company : "";
    }

    // Connection management
    public void addConnection(User user) {
        if (user != null && !user.equals(this)) {
            connections.add(user);
        }
    }

    public void removeConnection(User user) {
        connections.remove(user);
    }

    public boolean isConnectedTo(User user) {
        return connections.contains(user);
    }

    public Set<User> getConnections() {
        return new HashSet<>(connections);
    }

    public int getConnectionCount() {
        return connections.size();
    }

    /**
     * Find mutual connections with another user.
     */
    public Set<User> getMutualConnections(User other) {
        if (other == null) {
            return Collections.emptySet();
        }
        Set<User> mutual = new HashSet<>(connections);
        mutual.retainAll(other.getConnections());
        return mutual;
    }

    // Request management
    public void addSentRequest(ConnectionRequest request) {
        sentRequests.add(request);
    }

    public void addReceivedRequest(ConnectionRequest request) {
        receivedRequests.add(request);
    }

    public List<ConnectionRequest> getSentRequests() {
        return new ArrayList<>(sentRequests);
    }

    public List<ConnectionRequest> getReceivedRequests() {
        return new ArrayList<>(receivedRequests);
    }

    public List<ConnectionRequest> getPendingReceivedRequests() {
        List<ConnectionRequest> pending = new ArrayList<>();
        for (ConnectionRequest request : receivedRequests) {
            if (request.isPending() && !request.isExpired()) {
                pending.add(request);
            }
        }
        return pending;
    }

    
    // Skills management
    public void addSkill(String skillName) {
        if (skillName != null && !skillName.trim().isEmpty()) {
            skills.putIfAbsent(skillName, new Skill(skillName));
        }
    }

    public Skill getSkill(String skillName) {
        return skills.get(skillName);
    }

    public Set<String> getCommonSkills(User other) {
        if (other == null) {
            return Collections.emptySet();
        }
        Set<String> common = new HashSet<>(skills.keySet());
        common.retainAll(other.skills.keySet());
        return common;
    }
        
    // Getters and Setters
    public String getUserId() {
        return userId;
    }

    public String getName() {
        return name;
    }

    public void setName(String name) {
        this.name = name;
    }

    public String getEmail() {
        return email;
    }

    public void setEmail(String email) {
        this.email = email;
    }

    public String getHeadline() {
        return headline;
    }

    public void setHeadline(String headline) {
        this.headline = headline;
    }

    public String getCompany() {
        return company;
    }

    public void setCompany(String company) {
        this.company = company;
    }

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;
        User user = (User) o;
        return userId.equals(user.userId);
    }

    @Override
    public int hashCode() {
        return userId.hashCode();
    }

    @Override
    public String toString() {
        return String.format("User{id=%s, name=%s, connections=%d}", 
                           userId, name, connections.size());
    }
}

/**
 * Status of a connection request.
 */
enum RequestStatus {
    PENDING,
    ACCEPTED,
    REJECTED,
    WITHDRAWN,
    EXPIRED
}

/**
 * Connection request between two users.
 */
class ConnectionRequest {
    private static int requestCounter = 0;
    
    private final String requestId;
    private final User sender;
    private final User receiver;
    private final String message;
    private RequestStatus status;
    private final LocalDateTime createdAt;
    private LocalDateTime updatedAt;

    public ConnectionRequest(User sender, User receiver) {
        this(sender, receiver, null);
    }

    public ConnectionRequest(User sender, User receiver, String message) {
        if (sender == null || receiver == null) {
            throw new IllegalArgumentException("Sender and receiver cannot be null");
        }
        if (sender.equals(receiver)) {
            throw new IllegalArgumentException("Cannot send connection request to yourself");
        }
        
        this.requestId = "REQ-" + (++requestCounter);
        this.sender = sender;
        this.receiver = receiver;
        this.message = message;
        this.status = RequestStatus.PENDING;
        this.createdAt = LocalDateTime.now();
        this.updatedAt = LocalDateTime.now();
    }

    /**
     * Accept the connection request.
     */
    public boolean accept() {
        if (status != RequestStatus.PENDING) {
            return false;
        }
        if (isExpired()) {
            status = RequestStatus.EXPIRED;
            return false;
        }
        
        status = RequestStatus.ACCEPTED;
        updatedAt = LocalDateTime.now();
        
        // Create bidirectional connection
        sender.addConnection(receiver);
        receiver.addConnection(sender);
        
        return true;
    }

    /**
     * Reject the connection request.
     */
    public boolean reject() {
        if (status != RequestStatus.PENDING) {
            return false;
        }
        
        status = RequestStatus.REJECTED;
        updatedAt = LocalDateTime.now();
        return true;
    }

    /**
     * Withdraw the connection request (by sender).
     */
    public boolean withdraw() {
        if (status != RequestStatus.PENDING) {
            return false;
        }
        
        status = RequestStatus.WITHDRAWN;
        updatedAt = LocalDateTime.now();
        return true;
    }

    public boolean isPending() {
        return status == RequestStatus.PENDING;
    }

    public boolean isExpired() {
        // Expire after 30 days
        return createdAt.plusDays(30).isBefore(LocalDateTime.now());
    }

    // Getters
    public String getRequestId() {
        return requestId;
    }

    public User getSender() {
        return sender;
    }

    public User getReceiver() {
        return receiver;
    }

    public String getMessage() {
        return message;
    }

    public RequestStatus getStatus() {
        return status;
    }

    public LocalDateTime getCreatedAt() {
        return createdAt;
    }

    public LocalDateTime getUpdatedAt() {
        return updatedAt;
    }

    @Override
    public String toString() {
        return String.format("ConnectionRequest{id=%s, from=%s, to=%s, status=%s}",
                           requestId, sender.getName(), receiver.getName(), status);
    }
}

/**
 * Skill representing a user's expertise.
 */
class Skill {
    private final String name;
    private final Set<User> endorsements;

    public Skill(String name) {
        this.name = name;
        this.endorsements = new HashSet<>();
    }

    public String getName() {
        return name;
    }

    public void addEndorsement(User user) {
        if (user != null) {
            endorsements.add(user);
        }
    }

    public int getEndorsementCount() {
        return endorsements.size();
    }

    public boolean isEndorsedBy(User user) {
        return endorsements.contains(user);
    }
}
