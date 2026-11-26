# Real-Time Gaming Leaderboard - Problem Statement

## Problem Statement
- **System to design:** A real-time gaming leaderboard system.
- **Core user value:** Players need to see their real-time rank, relative rank, and the global top players to stay engaged and competitive in tournaments.

## Functional Requirements
- **FR1:** Increment player score upon match win in real time.
- **FR2:** Retrieve the global Top 10 (or Top 100) players in real time.
- **FR3:** Return a specific player's exact global rank.
- **FR4:** Return a relative rank window (e.g., 4 ranks above and below the player).
- **FR5:** Support monthly tournament lifecycles (creation, active tracking, and archival).

## Non-Functional Requirements

| Requirement | Target |
|---|---|
| Latency | < 50ms P99 for score updates and rank lookups |
| Scale (Users) | 5M DAU, 25M MAU |
| Scale (Traffic) | 500 avg write QPS, 2,500 peak write QPS |
| Scale (Future) | Design should be capable of scaling up to 500M users and 250,000 QPS |
| Availability | 99.99% |
| Durability | Persistent disaster recovery must be supported via a durable data store (e.g., MySQL) |

## Constraints
- **Tie-breakers:** When multiple players have the same score, the player who achieved the score first should be ranked higher.
- **Accuracy:** The leaderboard must be highly accurate, avoiding lost score increments or rank inconsistencies.
- **Memory Limits:** The system needs an in-memory component for speed but must be designed carefully to manage memory costs, particularly as the system scales to hundreds of millions of users.

## Out of Scope
- Game logic and match-making algorithms.
- User profile management (avatar uploads, friends list).
- Payment/rewards disbursement based on tournament outcome.
- Client-side rendering logic or game client implementation.

## 🔗 Cross-links
- [Approach](APPROACH.md)
- [Design](DESIGN.md)
