# Real Company Case Studies

Deep-dive analyses of production systems at massive scale.


## 🧮 Pack-to-Case-Study Matrix

| HLD Project | Recommended Case Study |
|---|---|
| [Ad Click Aggregator](../04-hld-projects/ad-click-aggregator/) | [Amazon](./amazon-orders/) |
| [Chat/Messaging Service System](../04-hld-projects/chat-service/) | [WhatsApp](./whatsapp-messaging/) |
| [Content Delivery Network (CDN) System](../04-hld-projects/content-delivery-network/) | [Netflix](./netflix-streaming/) |
| [Digital Wallet & Transactional Ledger - Problem Statement](../04-hld-projects/digital-wallet/) | [Stripe](./stripe-ledger-engine/) |
| [Distributed Email Service (Gmail)](../04-hld-projects/distributed-email-service/) | [WhatsApp](./whatsapp-messaging/) |
| [Distributed Object Storage - Problem Statement](../04-hld-projects/distributed-object-storage/) | [Amazon](./amazon-orders/) |
| [Distributed Workflow Orchestrator - Problem Statement](../04-hld-projects/distributed-workflow-orchestrator/) | [Amazon](./amazon-orders/) |
| [E-commerce Backend - Problem Statement](../04-hld-projects/ecommerce-backend/) | [Amazon](./amazon-orders/) |
| [File Storage Service](../04-hld-projects/file-storage/) | [Amazon](./amazon-orders/) |
| [Problem Statement: Distributed Partitioned Commit Log Broker](../04-hld-projects/kafka-distributed-broker/) | [LinkedIn](./linkedin-feed/) |
| [Live Video Streaming Pipeline - Problem Statement](../04-hld-projects/live-video-streaming-pipeline/) | [YouTube](./youtube-video/) |
| [Metrics Monitoring](../04-hld-projects/metrics-monitoring/) | [Google Spanner](./google-spanner-truetime/) |
| [Multi-Region Active-Active Architecture — Problem Statement](../04-hld-projects/multi-region-active-active/) | [Google Spanner](./google-spanner-truetime/) |
| [Nearby Friends](../04-hld-projects/nearby-friends/) | [Uber](./uber-realtime/) |
| [News Feed / Timeline System](../04-hld-projects/news-feed/) | [Twitter](./twitter-timeline/) |
| [Notification Service](../04-hld-projects/notification-service/) | [WhatsApp](./whatsapp-messaging/) |
| [Online Auction System](../04-hld-projects/online-auction/) | [Amazon](./amazon-orders/) |
| [Payment System](../04-hld-projects/payment-system/) | [Stripe](./stripe-ledger-engine/) |
| [Proximity Service - Problem Statement](../04-hld-projects/proximity-service-yelp/) | [Uber](./uber-realtime/) |
| [Real-Time Gaming Leaderboard - Problem Statement](../04-hld-projects/realtime-gaming-leaderboard/) | [Uber](./uber-realtime/) |
| [Real-Time Metrics Platform](../04-hld-projects/realtime-metrics-platform/) | [Google Spanner](./google-spanner-truetime/) |
| [Ride Sharing Backend System](../04-hld-projects/ride-sharing/) | [Uber](./uber-realtime/) |
| [Search Autocomplete - Problem Statement](../04-hld-projects/search-autocomplete/) | [Airbnb](./airbnb-search/) |
| [Distributed Social Graph Engine (Meta TAO)](../04-hld-projects/social-graph-engine-tao/) | [Meta](./meta-memcache-tao/) |
| [Social Post Search System](../04-hld-projects/social-post-search/) | [Twitter](./twitter-timeline/) |
| [Stock Exchange Matching Engine](../04-hld-projects/stock-exchange-matching-engine/) | [Stripe](./stripe-ledger-engine/) |
| [Video Recommendations](../04-hld-projects/video-recommendations/) | [YouTube](./youtube-video/) |
| [Video Streaming Platform](../04-hld-projects/video-streaming/) | [Netflix](./netflix-streaming/) |
| [Web Crawler](../04-hld-projects/web-crawler/) | [Google Spanner](./google-spanner-truetime/) |

---

## 📚 Available Case Studies

| Company | System | Scale Baseline | Provenance | Key Challenge | Interview Relevance |
|---------|--------|----------------|------------|---------------|---------------------|
| [Twitter](twitter-timeline/) | Timeline Feed | 500M users, 6K tweets/sec | Historical/approximate; see [scale metrics](twitter-timeline/#scale-metrics) | Fan-out problem | News feed designs |
| [Netflix](netflix-streaming/) | Video Streaming | 230M users, 15% internet traffic | Historical/approximate; see [scale metrics](netflix-streaming/#scale-metrics) | CDN architecture | Video platforms |
| [Uber](uber-realtime/) | Real-time Matching | 100M rides/month | Historical/approximate; see [scale metrics](uber-realtime/#scale-metrics) | Geospatial indexing | Location-based apps |
| [WhatsApp](whatsapp-messaging/) | Messaging | 2B users, 100B msgs/day | Historical/approximate; see [scale metrics](whatsapp-messaging/#scale-metrics) | Concurrency at scale | Chat systems |
| [Instagram](instagram-feed/) | Photo Feed | 2B users, 95M photos/day | Historical/approximate; see [scale metrics](instagram-feed/#scale-metrics) | Feed ranking | Social platforms |
| [Airbnb](airbnb-search/) | Search & Booking | 7M listings, 300M nights/year | Historical/approximate; see [scale metrics](airbnb-search/#scale-metrics) | Concurrent bookings | Marketplace systems |
| [Spotify](spotify-streaming/) | Music Streaming | 500M users, 100M tracks | Historical/approximate; see [scale metrics](spotify-streaming/#scale-metrics) | Personalization | Audio streaming |
| [Amazon](amazon-orders/) | Order Processing | 12M orders/day, 300M products | Historical/approximate; see [scale metrics](amazon-orders/#scale-metrics) | Distributed transactions | E-commerce systems |
| [Stripe Ledger Engine](stripe-ledger-engine/) | Financial Ledger | Millions of transactions/day | Historical/approximate; see [scale metrics](stripe-ledger-engine/#scale-metrics) | Absolute correctness | Fintech systems |
| [YouTube](youtube-video/) | Video Platform | 500 hrs upload/min, 1B hrs/day | Historical/approximate; see [scale metrics](youtube-video/#scale-metrics) | Transcoding at scale | Video platforms |
| [LinkedIn](linkedin-feed/) | Professional Feed | 900M users, 1T Kafka msgs/day | Historical/approximate; see [scale metrics](linkedin-feed/#scale-metrics) | Graph-based ranking | Professional networks |
| [Google Spanner](google-spanner-truetime/) | Globally Distributed Database | Petabytes, multi-continent | Historical/approximate; see [scale metrics](google-spanner-truetime/#scale-metrics) | Strict serializability via TrueTime | Distributed databases |
| [ChatGPT](chatgpt-inference/) | Enterprise Assistant & Agent Platform | 5M+ business users | Current source-backed; see [scale metrics](chatgpt-inference/#scale-and-provenance-metrics) | Tool orchestration + tenant controls | GenAI assistants |
| [GitHub Copilot](github-copilot/) | Code Assist & Coding Agent | Paid-plan cloud agent, 59-minute session cap | Current source-backed; see [scale metrics](github-copilot/#scale-and-provenance-metrics) | Repository context + branch-contained agents | AI coding systems |
| [Discord](discord-messaging-storage/) | Message Storage | Trillions of messages stored | Current source-backed; see [scale metrics](discord-messaging-storage/#scale-metrics) | Hot partitions at chat scale | Chat/message storage design |
| [Snowflake](snowflake-data-warehouse/) | Cloud Data Warehouse | Petabytes per large customer, hundreds of millions of queries/day fleet-wide | Widely known public facts; see [provenance](snowflake-data-warehouse/#-provenance-and-sources) | Storage/compute separation | Data platforms/analytics |
| [Meta](meta-memcache-tao/) | Social Graph & Cache Tier | 1B+ reads/sec on the graph store (TAO paper, 2013) | Public papers; see [scale metrics](meta-memcache-tao/#scale-metrics) | Read-heavy graph serving | Caching strategies, social feeds |

---

## 🎯 How to Use These Case Studies

### For Learning
- Understand real-world trade-offs and evolution patterns
- See how companies solved scaling challenges over time
- Learn the "why" behind architectural decisions

### For Interviews
- Reference actual company architectures when designing similar systems
- Use specific numbers and technologies as historical baselines unless the row is marked current source-backed; name the date/provenance when quoting them
- Understand common patterns that apply across systems

### For Preparation
- Study the system matching your interview company
- If interviewing at Uber → study Uber case study
- If asked about news feeds → reference Twitter and Instagram

---

## 📈 Learning Path

### 🟢 Beginner
Start with simpler fan-out and feed problems:
1. **[Twitter Timeline](twitter-timeline/)** - Classic fan-out on write vs read
2. **[Instagram Feed](instagram-feed/)** - Photo storage and feed ranking
3. **[LinkedIn Feed](linkedin-feed/)** - Graph-based professional network

### 🟡 Intermediate
Infrastructure and reliability challenges:
4. **[Netflix Streaming](netflix-streaming/)** - CDN and video delivery
5. **[WhatsApp Messaging](whatsapp-messaging/)** - Real-time messaging at scale
6. **[Spotify Streaming](spotify-streaming/)** - Audio streaming and recommendations
7. **[YouTube Video](youtube-video/)** - Video transcoding and delivery

### 🔴 Advanced
Complex real-time, transactional, geospatial, and GenAI-agent systems:
8. **[Uber Real-time](uber-realtime/)** - Geospatial + real-time matching
9. **[Airbnb Search](airbnb-search/)** - Search + booking with concurrency
10. **[Amazon Orders](amazon-orders/)** - Distributed transactions at scale
10.5. **[Stripe Ledger Engine](stripe-ledger-engine/)** - Financial ledger with absolute correctness and idempotency
11. **[Google Spanner TrueTime](google-spanner-truetime/)** - Globally distributed strict serializability
12. **[ChatGPT Inference](chatgpt-inference/)** - Multi-tenant assistant, tools, and enterprise controls
13. **[GitHub Copilot](github-copilot/)** - Repository-aware code assistant and cloud coding agent

---

## 🔗 Related Repository Content

These case studies reference concepts from:

| Concept | Location | Used In |
|---------|----------|---------|
| Load Balancing | [03-hld-concepts/load-balancing/](../03-hld-concepts/load-balancing/) | All case studies |
| Caching | [03-hld-concepts/caching/](../03-hld-concepts/caching/) | Twitter, Instagram, Spotify |
| CDN | [03-hld-concepts/cdn/](../03-hld-concepts/cdn/) | Netflix, Instagram, YouTube |
| Message Queues | [03-hld-concepts/message-queues/](../03-hld-concepts/message-queues/) | WhatsApp, Twitter, LinkedIn, Amazon |
| Database Sharding | [03-hld-concepts/database-sharding/](../03-hld-concepts/database-sharding/) | All case studies |
| Strict Serializability | [03-hld-concepts/logical-clocks-truetime/](../03-hld-concepts/logical-clocks-truetime/) | Google Spanner |
| Distributed Transactions | [03-hld-concepts/distributed-transactions/](../03-hld-concepts/distributed-transactions/) | Amazon, Google Spanner |
| News Feed Design | [04-hld-projects/news-feed/](../04-hld-projects/news-feed/) | Twitter, Instagram, LinkedIn |
| Chat Service | [04-hld-projects/chat-service/](../04-hld-projects/chat-service/) | WhatsApp |
| Ride Sharing | [04-hld-projects/ride-sharing/](../04-hld-projects/ride-sharing/) | Uber |
| Video Streaming | [04-hld-projects/video-streaming/](../04-hld-projects/video-streaming/) | Netflix, YouTube |
| E-commerce Backend | [04-hld-projects/ecommerce-backend/](../04-hld-projects/ecommerce-backend/) | Amazon, Airbnb |
| Multi-Tenant Chat Assistant | [06-genai-systems/02-llm-hld-projects/multi-tenant-chat-assistant/](../06-genai-systems/02-llm-hld-projects/multi-tenant-chat-assistant/) | ChatGPT |
| GenAI Safety | [06-genai-systems/00-concepts/safety-governance/](../06-genai-systems/00-concepts/safety-governance/) | ChatGPT, GitHub Copilot |
| Repository Search | [03-hld-concepts/search-systems/](../03-hld-concepts/search-systems/) | GitHub Copilot |

---

## 📖 Case Study Structure

Each case study follows this structure:

1. **Problem Statement** - Business challenge, technical requirements, scale metrics
2. **Architecture Evolution** - How the system evolved from v1 to current (with diagrams)
3. **Key Design Decisions** - Major choices with rationale and trade-offs
4. **Technologies Used** - Stack breakdown with alternatives considered
5. **Trade-offs Made** - Consistency vs availability, cost vs performance, etc.
6. **Lessons Learned** - What worked, what didn't, key pivots
7. **Interview Relevance** - How to use this in your interviews

---

## 📚 Sources and References

These case studies are based on publicly available engineering blogs, conference talks, and papers:

- Twitter Engineering Blog
- Netflix Tech Blog
- Uber Engineering Blog
- WhatsApp Engineering posts
- Instagram Engineering Blog
- Airbnb Engineering Blog
- Spotify Engineering Blog
- Amazon Builders' Library
- YouTube Engineering Blog
- LinkedIn Engineering Blog
- OpenAI product pages, help-center articles, and system/platform announcements
- GitHub Docs and GitHub Blog product announcements
- QCon, Strange Loop, and other conference presentations
- Academic papers and patents

---

## 🧭 Section Navigation

| | |
|---|---|
| **Prerequisites** | [HLD Projects ←](../04-hld-projects/) · [HLD Concepts ←](../03-hld-concepts/) — understand system design patterns before studying real-world applications |
| **What's Next** | [GenAI Systems →](../06-genai-systems/) — LLM-powered system design · [Study Plans →](../resources/study-plans/) — structured revision guides |
| **Related** | [Cheatsheets](../resources/cheatsheets/) · [Interview Tips](../resources/interview-tips/) |

---

*Happy Learning! 🎉*
