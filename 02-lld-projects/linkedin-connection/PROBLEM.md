# LinkedIn Connection System

## Problem Statement

Design a social networking connection system similar to LinkedIn that allows users to connect, manage their network, and discover new connections through mutual contacts and recommendations.

---

## Functional Requirements

1. **User Profile**: Create and manage user profiles with skills and work experience
2. **Send Connection Request**: Send connection invitations to other users
3. **Accept/Reject Request**: Process incoming connection requests
4. **Connection List**: View and manage existing connections
5. **Mutual Connections**: Find mutual connections between two users
6. **Connection Recommendations**: Suggest potential connections based on network
7. **Connection Degree**: Identify 1st, 2nd, and 3rd degree connections
8. **Endorsements**: Endorse connections for specific skills

---

## Non-Functional Requirements

1. **Scalability**: Handle millions of users and connections
2. **Performance**: Fast mutual connection queries (< 100ms)
3. **Concurrency**: Handle simultaneous connection requests
4. **Consistency**: Ensure bidirectional connections are consistent
5. **Availability**: High availability for connection operations

---

## Constraints & Assumptions

- Connections are bidirectional (if A connects to B, B is connected to A)
- Maximum 30,000 connections per user
- Connection requests expire after 30 days
- Only 1st degree connections can endorse each other
- Recommendation algorithm considers mutual connections, shared skills, same company

---

## Sample Interactions

```
1. Alice sends connection request to Bob
2. Bob receives notification of pending request
3. Bob accepts the connection request
4. Both Alice and Bob are now 1st degree connections
5. Charlie views Bob's profile - sees "10 mutual connections"
6. Charlie gets recommendation: "People you may know: Bob (5 mutual connections)"
7. Alice endorses Bob for "Java Development"
8. Bob's profile shows "Alice endorsed you for Java"
```

---

## Clarifying Questions to Ask

1. "Should connections be bidirectional or can they be one-way (like Twitter follows)?"
2. "What data should be stored in the user profile?"
3. "How many connection recommendations should we show?"
4. "Should we track when connections were made?"
5. "Is there a limit on pending connection requests?"
6. "Do we need to support blocking users?"
7. "Should we support connection messages (like LinkedIn notes)?"
8. "How do we handle withdrawn connection requests?"

---

## Entities to Identify

| Entity | Responsibility |
|--------|---------------|
| User | Profile data, skills, connections |
| Connection | Relationship between two users |
| ConnectionRequest | Pending invitation with status |
| Skill | Endorsable competency |
| Endorsement | Skill validation from connection |
| NetworkService | Connection operations, recommendations |

---

## Version Roadmap

| Version | Features |
|---------|----------|
| v1-basic | Users, connections, send/accept requests |
| v2-extended | Mutual connections, recommendations, endorsements |
| v3-optimized | Thread-safe, graph-based algorithms, caching |
