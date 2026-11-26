# Code Walkthrough: LinkedIn Connections

## Overview

Social network with connection degrees and recommendations.

---

## Core Entities

| Entity | Attributes |
|--------|------------|
| User | profile, connections, skills |
| Connection | user1, user2, status |
| Profile | name, headline, experience |

---

## Connection Degrees

```
You ──1st──> Direct connections
     ──2nd──> Friends of friends  
     ──3rd──> Friends of friends of friends
```

---

## Key Algorithms

### BFS for Connection Degree

```java
int getConnectionDegree(User from, User to) {
    Queue<User> queue = new LinkedList<>();
    Map<User, Integer> distance = new HashMap<>();
    
    queue.add(from);
    distance.put(from, 0);
    
    while (!queue.isEmpty()) {
        User current = queue.poll();
        if (current == to) return distance.get(current);
        
        for (User connection : current.getConnections()) {
            if (!distance.containsKey(connection)) {
                distance.put(connection, distance.get(current) + 1);
                if (distance.get(connection) <= 3) {
                    queue.add(connection);
                }
            }
        }
    }
    return -1; // Not connected
}
```

### Mutual Connections

```java
Set<User> getMutualConnections(User u1, User u2) {
    Set<User> connections1 = u1.getConnections();
    Set<User> connections2 = u2.getConnections();
    
    Set<User> mutual = new HashSet<>(connections1);
    mutual.retainAll(connections2);
    return mutual;
}
```

---

## Interview Questions

### 1. "How to recommend connections?"

```java
List<User> getRecommendations(User user) {
    Map<User, Integer> scores = new HashMap<>();
    
    for (User connection : user.getConnections()) {
        for (User fof : connection.getConnections()) {
            if (fof != user && !user.isConnected(fof)) {
                scores.merge(fof, 1, Integer::sum);
            }
        }
    }
    
    return scores.entrySet().stream()
        .sorted(Map.Entry.<User, Integer>comparingByValue().reversed())
        .limit(10)
        .map(Map.Entry::getKey)
        .collect(toList());
}
```

### 2. "How to handle connection requests?"

```java
enum ConnectionStatus { PENDING, ACCEPTED, REJECTED }

class ConnectionRequest {
    User sender;
    User receiver;
    ConnectionStatus status;
    
    void accept() {
        sender.addConnection(receiver);
        receiver.addConnection(sender);
        status = ACCEPTED;
    }
}
```

### 3. "How to show mutual connections count efficiently?"

Pre-compute and cache, update on connection changes.

---

## Complexity

| Operation | Time |
|-----------|------|
| getMutualConnections | O(C) |
| getConnectionDegree | O(V + E) |
| getRecommendations | O(C × C_avg) |

Where C = connections, V = users, E = edges
