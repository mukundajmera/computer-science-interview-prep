# Meta Memcache and TAO Case Study

This case study covers two generations of one system: the memcache tier that scaled the world's largest read-heavy workload in front of MySQL, and TAO, the purpose-built graph store that grew out of it. Both are documented in public USENIX papers, which makes them unusually reliable ground for interview preparation: the mechanisms, the failure modes, and the scale figures all come from the people who ran the system. Read section 3 for the caching machinery every candidate is expected to know (leases, invalidation, failover), and section 4 for the graph-store design that turns the same ideas into a product API.

## 1. Problem Statement

Meta (Facebook at the time of the papers) had to serve one of the largest read-heavy workloads ever built: the social graph. Nearly every page view assembles posts, profiles, likes, comments, and friend connections in real time, so the serving path is dominated by reads over graph-shaped data.

### Business Challenge
A social product lives or dies on page-load latency. Every render fans out to dozens or hundreds of small lookups: who are my friends, what did they post, who liked it, what privacy settings apply. The working set is far too large for one database machine, the read-to-write ratio is extreme, and the data is naturally a graph, not a set of independent rows. The platform also grew through several orders of magnitude of users without being allowed a redesign-and-rebuild pause.

That last constraint is easy to underrate. The architecture described here was not drawn on a whiteboard and then built; it was accumulated in production while the load kept doubling. Every mechanism in this case study has the shape of an answer to an incident or a looming limit, which is why the design rewards study: it shows what a read-heavy serving layer looks like after reality has edited it.

### Technical Requirements
- **Read-heavy serving:** The overwhelming majority of requests are reads, and each page needs many of them.
- **Graph access patterns:** The core queries are "this object" and "the edges of this type from this object, newest first."
- **Low tail latency:** A single page fans out to hundreds of lookups, so the slowest lookup sets the page time.
- **Multi-region operation:** Users are global; data must be served close to them without giving up a single writeable source of truth.
- **Elastic caching:** The cache tier must survive hot keys, failed servers, and whole failed clusters without taking the databases down with it.

### Constraints Imposed by the Product
Two product facts quietly shape everything that follows. First, the data is social: most of it is read by people other than its author, so reads outnumber writes by orders of magnitude and the read path deserves most of the engineering budget. Second, the product is forgiving in a specific way: a friend seeing a like count that is a few seconds old is invisible, while a page that loads slowly or fails is not. That asymmetry is what makes bounded staleness a resource the architecture can spend. A different product (payments, reservations) has the opposite asymmetry, and this case study's choices would be wrong there, a point section 11 returns to.

### Scale Metrics
Numbers below are tied to the two public papers listed in Sources; where a figure is not in a paper, it is labelled.

- **TAO serving load:** More than a billion reads per second and millions of writes per second, on a dataset of many petabytes (TAO paper, USENIX ATC 2013).
- **Memcache tier:** Facebook described processing billions of requests per second through its memcache deployment (memcache paper, NSDI 2013).
- **Users:** Facebook publicly announced crossing one billion monthly active users in late 2012, the period these papers describe.
- **Fan-out per page:** A single page render may require hundreds of backend lookups (described qualitatively in the memcache paper); treat any specific per-page count as an illustrative estimate.
- **Read-to-write ratio:** Reads dominate by orders of magnitude; the memcache paper motivates the entire design from that asymmetry.

### Capacity Arithmetic (Illustrative Estimate)
The numbers above imply per-machine loads worth doing arithmetic on in an interview. Suppose the memcache tier serves on the order of one billion requests per second across on the order of ten thousand cache servers (server count is an illustrative estimate, not a published figure): 1,000,000,000 / 10,000 = 100,000 requests per second per server. A get is a hash lookup and a network write, so 100k small ops per second per server is comfortable for memory but aggressive for network: at an illustrative average response size of 1 KB, that is 100,000 * 1 KB = 100 MB/s of egress per server, roughly a gigabit per second just for cache responses.

This is why the paper cares about UDP connection state, response batching, and incast windows: at this rate, per-packet and per-connection overheads are the bottleneck, not CPU or DRAM.

The same arithmetic explains the fan-out concern. If one page needs an illustrative 300 backend lookups and the site renders an illustrative 3 million pages per second fleet-wide, the backend sees 300 * 3,000,000 = 900 million lookups per second, which lands exactly on the published order of magnitude. The tail-latency point follows too: the page finishes when its slowest lookup finishes, so the 99th percentile of a single lookup is roughly the 1 in 300 event for the page.

---

## 2. Architecture Evolution

### Phase 1: Databases Only
The early site ran on MySQL with web servers querying it directly. This works until read traffic outgrows what the databases can serve; adding replicas helps reads but cannot fix the fundamental cost of a disk-backed B-tree lookup per query at this fan-out. The breaking point is not total throughput so much as the product of fan-out and users: when each page needs hundreds of row lookups and millions of pages render per second, no realistic number of database replicas keeps up, and every replica added multiplies the write-propagation work as well.

### Phase 2: Look-Aside Memcache Tier
The first scaling answer was a look-aside cache in front of MySQL: web servers check memcache first, and on a miss they read the database and fill the cache. This is the architecture the 2013 memcache paper describes at maturity: a geographically distributed deployment with clusters, regional pools, and cross-region invalidation, hardened over years against hot keys, stale reads, and cascading failures. The important point about this phase is that it was not one design decision but an accumulation: leases, gutter pools, regional pools, and warmup routes were each added in response to a specific observed failure, and the paper reads as a field guide to what actually breaks a demand-filled cache at scale.

### Phase 3: TAO, a Purpose-Built Graph Store
Look-aside memcache over sharded MySQL left two gaps: graph traversals were awkward (application code stitched objects and edges together by hand), and the cache API was a generic key-value interface with no notion of associations. TAO replaced the ad-hoc layering with a single geographically distributed data store that exposes objects and associations directly, keeps its own write-through cache tiers, and still uses MySQL for durable storage underneath. The memcache paper's look-aside tier and TAO coexist as two generations of the same idea: move the read path to memory, keep writes simple and durable.

---

## 3. The Memcache Tier in Depth

### Look-Aside Caching
The serving pattern is demand-filled look-aside: read from cache, on miss read the database and set the cache entry. Writes invalidate by deleting the key. The cache never decides truth; the database does. This keeps the consistency model understandable: a read can be stale, but the database is always authoritative.

### Leases: The Two Bugs They Fix
The paper names two pathologies that leases solve:

1. **Stale sets.** A cache miss causes a database read; before the fill happens, another writer updates the database and deletes the key. The late fill then writes an old value back into the cache, where it can live until the next delete. With leases, a miss returns a token bound to the key; the fill is accepted only if the token is still current. A delete or a newer lease invalidates earlier tokens, so the stale fill is rejected.
2. **Thundering herds.** A hot key expires or is deleted; thousands of requests miss simultaneously and all hammer the database for the same row. With leases, the first misser gets a token and the right to fill; subsequent missers are told to wait briefly and retry the cache instead of querying the database. One database read serves the whole herd.

Leases convert a correctness race and a load spike into a short wait, which is exactly the right trade for a read-heavy path.

### A Lease Timeline, Step by Step
Walking one hot key through an expiry makes the mechanism concrete:
1. Key `profile:42` expires. Requests keep arriving at thousands per second.
2. The first request to miss asks memcache for a lease. Memcache records a new lease for the key and hands back a token, say token number 7.
3. The second through ten-thousandth requests miss in the same instant. Memcache sees a live lease and, instead of a token, tells each of them to wait a short, fixed interval and retry the cache.
4. The token holder reads the row from MySQL and issues a set carrying token 7. Because no delete or newer lease has occurred, the set is accepted. The waiters retry, hit, and the herd never reaches the database.
5. The stale-set variant: suppose that while the token holder is still reading MySQL, a writer updates profile 42 and deletes `profile:42`. The delete invalidates token 7. When the slow reader finally sets with token 7, memcache rejects it. The next request misses, gets token 8, and fills the fresh value. Without tokens, step 5's stale set would have silently overwritten the fresh data.

Note what the design deliberately does not do: there is no lock service, no queue, and no coordination between web servers. The lease is a counter inside the cache that already holds the key, which is why it costs almost nothing to add to the hot path.

### Layout: Clusters, Regional Pools, and Regions
- **Cluster:** A set of web servers and a set of memcache servers inside one datacenter building. Keys are sharded across the memcache servers of the cluster by consistent hashing on the key.
- **Regional pools:** Within a region, multiple front-end clusters share one *regional pool* of memcache servers for keys that are slow-changing but read everywhere (for example, user profile data). Replicating such keys in every cluster would multiply invalidation traffic and memory use; the regional pool stores each once.
- **Regions:** A region is a full geographic footprint with its own databases and cache tiers. One region is the master for writes; the others hold replicas and serve local reads.

### Cross-Region Invalidation with mcsqueal
When a write commits in the master region, every replica region's caches must be told to drop the old value. The mechanism described in the paper is an invalidation daemon (mcsqueal) deployed with the databases: it inspects committed SQL statements, extracts the deletes that each statement implies, and broadcasts those deletes to the memcache servers in its region. Batching and pipelining these packets matters: at this write rate, per-statement round trips would not keep up.

### Keys, Values, and What Actually Gets Cached
The memcache tier caches whatever the application layer can serialize: rendered fragments, row-shaped records, counts, and lists of IDs. Keys are namespaced by product and type so that different teams share the tier without collisions, and values are opaque byte strings to the cache itself. Two consequences matter for interviews. First, because values are opaque, the cache cannot help with partial updates: changing one field means invalidating the whole entry, which is why small, read-together values cache best. Second, because the tier is shared, its protections (leases, regional pools) apply uniformly to every product, which is precisely why a single team's hot key does not take down an unrelated team's data.

### Why Placement Has Three Levels
The three placements (cluster-local memcache, regional pool, and TAO's follower/leader tiers) answer the same question at different scales: how many copies of a popular value should a region hold? A worked comparison makes the trade concrete (illustrative estimate, arithmetic shown). Suppose a region runs 8 front-end clusters and a slow-changing profile record is read everywhere. Cluster-local caching holds 8 copies and, on each write, delivers 8 invalidations, one per cluster. The regional pool holds 1 copy and takes 1 invalidation, but every read now crosses cluster boundaries to reach the shared pool, adding network hops.

The design resolves this by access pattern: fast-changing keys stay cluster-local (invalidation traffic would dominate any sharing), slow-changing keys move to the regional pool (the copy count and invalidation savings win), and graph data with structured access goes to TAO, where the follower/leader split plays the same game inside one system. The interview takeaway is that cache placement is a knob per access pattern, not a global setting, and the cost model is copy count times invalidation rate versus added read latency.

### Resilience Details Worth Naming in an Interview
- **Cold cluster warmup:** A new or drained cluster would miss on nearly every request and crush the database. Clients in a cold cluster are allowed, on a miss, to fetch from a warm cluster's cache and fill locally, so the new cluster heats up without touching the database for most keys.
- **Gutter servers:** A small spare pool of memcache servers. When a regular server fails, its keys' clients fail over to gutter servers, which query the database and hold the data briefly. This bounds the database load from a single server loss instead of letting the failed shard's full traffic hit MySQL.
- **UDP for gets, TCP for sets:** Reads use a connectionless UDP path through the routing layer to cut latency and per-server connection state; writes and invalidations take the reliable TCP path where ordering and delivery matter.
- **Incast congestion control:** One web server requesting many keys at once can get many large responses arriving simultaneously and overflowing switch buffers. The memcache servers apply a sliding-window limit on in-flight response data per client to smooth the burst.

---

## 4. TAO: The Graph Store

### Data Model
TAO exposes two primitives, both identified by 64-bit integers:
- **Objects:** Typed nodes (a user, a post, a comment, a check-in), each a set of key-value fields.
- **Associations:** Typed, directed edges between objects (FRIEND, LIKE, COMMENT_ON), each with a timestamp and optional payload, and each automatically queryable in reverse where the product needs it.

This matches the workload directly: rendering a page is a handful of object reads plus bounded association queries such as "the 50 most recent comments on this post" or "the count of likes."

### Storage Layer
Durable storage is sharded MySQL. The 64-bit ID space is divided into shards; each object lives in the shard its ID maps to, and each association lives in the shard of its source object, so the common query "edges out of this object" is a single-shard lookup. Thousands of database servers hold the full dataset.

### Cache Tiers: Leaders and Followers
Above the databases, TAO runs two cache levels per region:
- **Leader tier:** A small set of leader cache servers, one authoritative leader per shard. Leaders serialize all writes for their shards, read from and write through to MySQL, and emit refill or invalidate messages to followers after each write.
- **Follower tiers:** Multiple tiers of follower cache servers sit between clients and leaders. Clients talk only to followers. A follower answers hits from memory, forwards misses to its shard's leader, and applies the leader's asynchronous invalidation and refill messages.

### Write Path
A write goes from the client to a follower, to the shard's leader, and synchronously through the leader to MySQL. Only after the database commit does the leader acknowledge success and then propagate the change to followers. Because the leader serializes its shard's writes and always writes through, the databases stay authoritative and the cache can never diverge in a way that a single leader cannot repair.

### Consistency Model
TAO deliberately provides per-shard sequential consistency and eventual consistency across tiers and regions. A client that writes and then re-reads its own shard sees its write; a different client in another tier may briefly see the old value. The paper's position is that this is the right trade for the product: the social graph tolerates seconds-scale staleness almost everywhere, and buying strong global consistency would cost latency and availability on every single read.

### The API Surface
The read API is intentionally narrow, and the narrowness is the optimization surface:
- **Object reads:** fetch the fields of one object, or of a list of objects in one round trip.
- **Association queries:** `assoc_get` returns edges of one type out of one object, optionally bounded by a time range and a limit, which is exactly the shape of "the 50 most recent comments on this post."
- **Association counts:** `assoc_count` answers "how many likes" without transferring the edge list; counts are cached and adjusted on writes rather than recomputed.
- **Reverse edges:** where the product needs "all posts that liked this user"-style queries, TAO maintains the inverse association so both directions stay single-shard lookups anchored at the right object.

Because every query in the API maps to a bounded, single-shard access pattern, the store can reason about cost: there is no unbounded traversal, no ad-hoc join, and no query that an application can accidentally make expensive. Products that need arbitrary graph walks build them out of these bounded steps, one hop per call.

### Multi-Region Geometry
TAO extends the leader/follower idea across regions. Each shard has one master region at a time; in that region the leader tier talks to the writable MySQL copy. Other regions run follower tiers over local read replicas, and invalidations flow from the master's leaders through the replication stream to remote followers. A user in a follower region who writes pays a cross-region round trip to the shard's master, but that same user's friends, who mostly read, are served entirely from local memory and local replicas. The geometry is the same bet the whole case study makes: writes can travel, reads must be local.

### Write Examples and What the Follower Sees
Two concrete writes show the machinery working:
- **A user posts a comment.** The client sends the create to a follower, which forwards it to the source object's shard leader. The leader writes the association row to MySQL, commits, acknowledges to the client, and then sends refill messages to the followers that cache that association list. A friend refreshing the post a moment later either sees the new comment (if their follower has applied the refill) or, briefly, the old list. The window is the asynchronous hop, typically small.
- **A user changes their name.** The object write goes through the same leader path. Followers holding the old object are invalidated. If the same user immediately views their own profile, per-shard sequential consistency means their read, routed to the same shard's chain, reflects the change. A different user may see the old name until the invalidation arrives.

The pattern to carry into an interview: the write is acknowledged only after the durable commit, and everything after the commit is propagation. Correctness is decided at one point, by one leader, at one database.

---

## 5. Failure Modes and How the System Handles Them

### End-to-End Read Walkthrough
Before enumerating failures, trace one healthy page render so the failure modes have a baseline. A user opens a friend's profile in a follower region:
1. The web server issues a batch of TAO reads: the friend's user object, the association query for their recent posts, and like and comment counts for each post.
2. Each request lands on a follower cache. Most hit: the profile object and the popular posts are read constantly and live in follower memory.
3. A few miss. Those followers ask the shard's leader; the leader usually hits its own memory because it aggregates misses for the whole region. The rare leader miss reads the local MySQL replica.
4. The responses return through the followers, which fill their caches as they answer, so the next reader of the same data is a memory hit at the closest tier.
5. Behind this, TAO-independent data (say, a rendered sidebar fragment) comes from the memcache tier with the same hit pattern, protected by leases for its hot keys.
Total database touches for the whole page: near zero. That is the design goal, and every failure mode below is a way this walkthrough can be forced down a slower path.

- **Single memcache server failure:** Clients fail over to gutter servers, which absorb the failed shard's traffic with short-lived database-backed fills, bounding database load until the server returns.
- **Hot key expiry:** Leases admit one database fill per expiry and make the rest of the herd wait and retry, so a popular key's expiration is a small blip instead of a database stampede.
- **Stale cache race:** Lease tokens make late fills no-ops; a value older than the newest invalidation cannot be reinstalled.
- **Cold or rebuilt cluster:** Warm-cluster reads on a miss let the cold cluster serve and fill from a healthy cluster's memory instead of the database.
- **Follower failure in TAO:** Other followers in the tier take over by consistent-hash remap; followers are stateless caches, so nothing is lost.
- **Leader failure in TAO:** A follower is promoted to lead the shard; writes for that shard pause or reroute briefly while leadership moves. Reads can continue from other tiers and, if needed, directly from the database.
- **Database shard failure:** MySQL replication promotes a replica. Reads for that shard degrade to cache-only until the shard is writable again; the paper describes explicitly favoring availability of reads over writes in this window.
- **Cross-region link problems:** Replica regions keep serving local reads from their caches and replica databases; invalidation traffic queues and catches up when the link heals. Staleness grows during the outage, which is the accepted price of keeping every region readable.
- **Invalidation daemon lag:** If mcsqueal falls behind, replica regions serve stale data longer. The mitigation is operational (batching, monitoring lag) rather than a protocol change, again choosing simplicity over stronger guarantees.

### The Cascading Failure These Mechanisms Prevent
It is worth tracing what happens without them, because the failure is multiplicative. One memcache server holds roughly 1/N of the keys in an N-server cluster. When it dies, every request for those keys misses at once and lands on the databases. If the databases slow down under the new load, cache fills take longer; slower fills mean more outstanding misses; more misses mean more database load.

The memcache paper's resilience mechanisms each cut one link in this chain: gutter caps how much new load a single server loss can add, leases cap how much load one hot key can add, and warmup routes cap how much load a whole cold cluster can add. The design principle generalizes: in a demand-filled cache, every failure converts cache traffic into database traffic, so resilience mechanisms are really database-protection mechanisms.

---

## 6. Key Design Decisions, and What Was Rejected

| Decision | Chosen | Rejected Alternative | Why the Rejection |
| :--- | :--- | :--- | :--- |
| Cache style | Look-aside, demand-filled | Cache-aside with the cache as write-through coordinator | The database must stay the single authority; a smarter cache becomes a second consistency problem |
| Hot-key protection | Leases (tokens plus brief waits) | Request coalescing with explicit locks | Locks across a fleet of web servers are a distributed-locking system of their own; leases need no extra service |
| Slow-changing shared data | One regional pool shared by clusters | Replicate those keys in every cluster | Replication multiplies memory and invalidation traffic for keys that rarely change |
| Failed-server handling | Small gutter pool | Immediate consistent-hash remap to the remaining servers | Remapping shifts the entire failed shard's load onto the database at once; gutter absorbs it gradually |
| Get transport | UDP with a thin routing layer | TCP everywhere | Per-connection state and latency matter at billions of gets per second; sets keep TCP where reliability matters |
| Graph API | Objects plus typed associations in one store (TAO) | Keep generic key-value memcache and assemble graphs in application code | Application-side stitching duplicates traversal logic in every product and cannot optimize association queries centrally |
| TAO write path | Leader serializes and writes through to MySQL | Multi-writer with conflict resolution | A single leader per shard makes the consistency story explainable; multi-writer buys little at this read-to-write ratio |
| Cross-tier consistency | Asynchronous invalidation, eventual | Synchronous multi-tier write coherence | Synchronous coherence puts cross-region latency on every write and couples the availability of all tiers |

---

### Two Decisions Worth Defending in a Room
Interviewers often push on these two specifically, so it helps to have the defense ready:
- **Deleting instead of updating cached values.** When data changes, the cache entry is deleted, not overwritten. An update-in-place would race: the update could arrive at a cache server before or after a concurrent fill from a stale database read, and ordering them requires version coordination the protocol does not have. A delete is idempotent and order-tolerant: worst case, the next reader refills from the authoritative store. This is why mcsqueal ships deletes, and it generalizes: prefer invalidation over propagation wherever the store of record can refill cheaply.
- **A single leader per shard instead of quorum writes.** A quorum protocol would raise write availability during leader failover at the price of an entirely new consistency stack: memberships, epochs, read repair. Given a read-dominated workload and a product that tolerates brief write pauses per shard, a single serializing leader plus fast failover is dramatically simpler to reason about and to operate. The defense is the workload: if writes were the scarce resource, the trade would flip.

## 7. Technologies

| Layer | Technology | Role |
| :--- | :--- | :--- |
| Durable storage | Sharded MySQL | Authoritative store for objects, associations, and the data behind memcache |
| Cache | memcached (heavily extended in-house) | In-memory look-aside tier and TAO's leader/follower caches |
| Routing | In-house routing layer (described publicly as mcrouter in later write-ups) | Sharding keys across cache servers, UDP get path, failover |
| Invalidation | mcsqueal daemon | Turns committed SQL into batched cache deletes across regions |
| Identity | 64-bit ID space with shard mapping | Single-hop placement for objects and associations |
| Client path | Web tier with batched, parallel backend requests | Bounds page latency by overlapping the fan-out of hundreds of lookups |
| Replication | MySQL replication within and across regions | Feeds local read replicas and carries the write stream that invalidations follow |

---

## 8. Trade-offs Made

A note on vocabulary before the table: several terms in this area are used loosely in interviews and precisely in the papers. **Look-aside** means the application checks the cache and fills it on a miss; the cache never talks to the database itself. **Write-through** means the write passes through the cache layer to the store before being acknowledged, which is what TAO's leaders do. **Write-behind** (batching writes in the cache and flushing later) appears nowhere here, because it would make the cache part of the durability story, which both papers refuse. Using these three terms correctly, and noticing which one a system actually implements, is a fast way to establish credibility.

1. **Staleness for availability:** Every design layer accepts bounded staleness (leases, asynchronous invalidation, eventual cross-tier consistency) because a read-heavy social product loses more from latency and outages than from seconds-old data.
2. **Simplicity of authority for cache cleverness:** The database remains the only writer of truth. The cache tiers accumulate mechanisms (leases, gutter, regional pools) precisely so that the authority story never has to change.
3. **Specialized graph store for API leverage:** TAO narrows the interface to objects and associations. Products that do not fit the model need other systems, but everything that does fit gets caching, sharding, and traversal for free.
4. **Single-master writes for a global read fleet:** One writeable region simplifies conflict handling; every other region pays read-your-own-write latency for writes that must travel to the master. TAO papers over this with per-shard leadership, but the fundamental geometry remains.
5. **Operational machinery for protocol simplicity:** mcsqueal, warmup routes, and gutter pools are extra moving parts, chosen so that the cache protocol itself can stay a tiny get/set/delete surface.
6. **Generality of the cache tier for product velocity:** The memcache tier serves every team with one shared mechanism, including its quirks (leases, regional pools), rather than letting each product team tune a private cache. Teams ship features without each one re-solving herds and invalidation, at the cost of accepting the tier's one-size-fits-all policies.
7. **MySQL as the durable substrate for a graph store:** TAO could have been built on a custom storage engine, but keeping MySQL meant inheriting mature replication, backup, and operational knowledge. The cost is that graph-shaped access has to be mapped onto relational storage, which the cache tiers then work to hide.

---

## 9. Lessons Learned

- **Design for the read path first.** When reads outnumber writes by orders of magnitude, every dollar spent making reads cheap and local pays back on every page view.
- **Thundering herds are a correctness-adjacent problem.** The herd does not return wrong data; it takes the site down. Leases fix both the herd and the stale-set race with one mechanism, which is why they are the classic interview takeaway.
- **Keep one source of truth and make caches defer to it.** Every failure mode above is handled by making the cache disposable, not by making it smarter about truth.
- **Match the API to the workload.** A graph workload on a key-value API pushes traversal complexity into every client; a small, typed API (objects, associations, counts) centralizes it where it can be optimized.
- **Eventual consistency is a product decision.** The papers are explicit that the social product tolerates staleness, and the architecture spends that tolerance on latency and availability. Naming what your product can tolerate is a prerequisite for the design, not an afterthought.
- **Failover should bound blast radius, not just restore service.** Gutter servers and warm-cluster reads exist so that failures degrade gracefully instead of shifting full load onto the next layer down.
- **Do the arithmetic on the boring parts.** The interesting bottlenecks at this scale were packets per second, switch buffers, and connection tables, not exotic algorithms. Interviewers reward candidates who estimate per-server rates before reaching for mechanisms.
- **Narrow APIs are a performance feature.** TAO's small query surface makes every access pattern bounded and cacheable; a general query language would have made the caching layer's job impossible to reason about.
- **Hot keys are a permanent condition, not an incident.** With billions of users, some data is always celebrity-scale. Mechanisms that assume a roughly uniform key distribution fail in production even when they pass in testing.
- **Two generations of a system can teach more than either alone.** The look-aside tier and TAO embody the same bet with different APIs. Studying why the second was built, and what it deliberately kept from the first, is a repeatable way to read any mature architecture.

---

## 10. What to Say in an Interview

### Question 1: A cache key expires and ten thousand requests miss at once. What happens, and how do you prevent it?
**Strong answer:** Without protection this is a thundering herd: every misser queries the database for the same row, and the load spike can cascade. The memcache paper's answer is a lease. On a miss, the cache hands the first requester a lease token and the right to fill; later missers are told the key is being filled and to wait briefly, then re-read from cache. Only the token holder's fill is accepted, which also closes the stale-set race where a slow fill reinstalls a value newer writers have already invalidated. Mention both bugs, because leases exist for both: the herd (load) and the stale set (correctness). Bonus: name request coalescing as the same idea in other stacks, and note that the lease mechanism lives inside the cache server itself, so it adds no external coordination service to operate or to fail.

### Question 2: Walk the read and write paths of a social graph store like TAO.
**Strong answer:** Reads go client to follower cache; on a hit the follower answers. On a miss the follower asks the shard's leader, which reads MySQL, fills itself, and answers through the follower. Writes go client to follower to the shard's leader, which writes through to MySQL, commits, and only then acknowledges, afterwards sending asynchronous refill or invalidate messages to followers. Placement is by 64-bit ID shard: objects in their own shard, associations in the source object's shard, so "edges out of this node" is single-shard. Consistency is per-shard sequential, eventual across tiers. The points that separate a strong answer: the leader serializes writes per shard, write-through keeps MySQL authoritative, and followers are disposable stateless caches. If asked why associations live with the source object: the dominant query is always "edges out of this node, newest first," and co-locating the edge list with its source keeps that query to one shard and one cache key prefix. A query in the opposite direction is served by a separately maintained inverse association, so neither direction ever requires a scatter-gather across shards.

### Question 3: How do you keep caches in replica regions from serving stale data after a write in the master region?
**Strong answer:** Writes commit in the master region's databases. An invalidation daemon deployed with those databases inspects each committed SQL statement, derives the cache keys it affects, and broadcasts batched delete messages to the memcache servers in its region; replication plus local invalidation daemons propagate the same deletes in replica regions. Deletes, not sets, travel: shipping new values would race with concurrent writes, while a delete just causes the next reader to refill from its local replica, which is already consistent with the commit order. Accept the remaining staleness window explicitly and monitor invalidation lag as the operational signal. If the interviewer asks why the daemon reads committed SQL rather than having applications emit invalidations directly: the database is the one place every write must pass through, so deriving invalidations there cannot be bypassed by a buggy or forgetful application, and it moves the concern out of product code entirely.

### Question 4: When would you bypass or not add a cache like this at all?
**Strong answer:** Three cases. First, when the workload is write-dominated or read-once: caching data nobody re-reads only adds invalidation cost. Second, when the product truly cannot tolerate staleness, for example balance-like invariants: serve those from the authoritative store with its own scaling story, the way the Stripe ledger case study keeps balances correct by construction. Third, when the dataset is small enough that the database already meets the latency target: a cache tier is operational machinery (warmup, gutter, invalidation pipelines) and should be bought only when the read path needs it. A strong candidate frames caching as a trade purchased with a staleness budget, not a default, and names the budget the product can actually afford.

### Rapid-Fire Follow-Ups and One-Line Answers
- **Why not let applications write invalidations themselves?** Deriving deletes from committed SQL at the database cannot be bypassed by a buggy or forgetful application.
- **Why are followers disposable?** They hold no authoritative state, so losing one costs only a temporary hit-rate dip, never data.
- **What makes a key "hot" here?** Celebrity-scale data: a small set of objects read by a large fraction of users, which breaks uniform-load assumptions.
- **Why shard associations by source object?** The dominant query is edges out of one node; source sharding keeps it single-shard, and inverse associations cover the reverse direction.
- **What is the consistency guarantee, in one sentence?** Per-shard sequential consistency, eventual consistency everywhere else, chosen because the product tolerates staleness and prizes availability.
- **Where does this design spend money to save time?** Memory: the architecture is, at heart, a plan for keeping the working set in RAM close to users and paying for it with copies, invalidations, and operational machinery.
- **What happens to a write during a leader failover?** It waits or fails fast to the client; the design prefers a brief, visible write pause over accepting writes it cannot order correctly.
- **Why keep MySQL under TAO instead of a custom store?** It inherits battle-tested replication, backups, and operations, and the cache tiers hide the relational impedance for graph access.
- **What single number anchors the whole design?** The read-to-write ratio; every mechanism here is bought with the observation that reads dominate by orders of magnitude.

---

## 11. Interview Relevance

- **Caching interviews:** This is the reference deployment for look-aside caching, leases, hot-key handling, and invalidation design.
- **Social product system design:** News feed, messaging, and friend-graph questions all reduce to the access patterns TAO was built for.
- **Consistency discussions:** A concrete, well-documented example of choosing per-shard sequential plus global eventual consistency, with the product reasoning spelled out.
- **Failure-design discussions:** Nearly every mechanism here exists because a specific failure was observed in production, which makes this case study a strong source of "what breaks at scale" examples for any distributed-systems interview.
- **Pairs with:** The LinkedIn feed and Twitter timeline case studies for fan-out, the caching concept guide for fundamentals, and the social-graph-engine-tao HLD project for a guided design of the same problem.

### When This Architecture Does Not Fit
Being explicit about the boundary conditions strengthens an interview answer:
- **Strong-consistency domains:** Ledgers, reservations, and inventory for scarce goods cannot spend the staleness budget this architecture assumes. Those need serializable storage with its own scaling story.
- **Write-heavy telemetry:** Append-mostly event streams want log-shaped storage, not a read-optimized cache tier in front of rows.
- **Small systems:** Below the scale where the database alone meets latency targets, every mechanism in this case study is negative value: more moving parts, more operational surface, no bottleneck relieved.
- **Unbounded graph analytics:** Multi-hop analysis over the whole graph belongs in offline processing systems; TAO's API is deliberately too narrow for it, which is a feature for the serving path and a reason to use something else for analytics.

### Common Mistakes This Case Study Corrects
- **"Just add a cache" without an invalidation story.** The hard part of this architecture is not storing values in memory; it is the delete pipeline, the lease protocol, and the failure handling around them. An answer that adds a cache without saying how it stays fresh is incomplete.
- **Assuming cache and database must be strongly consistent.** Both papers chose bounded staleness on purpose and said so. Claiming the system is strongly consistent is a factual error about a well-documented design.
- **Forgetting the write path crosses regions.** It is easy to draw every user reading locally and forget that writes route to the shard's master region. The latency consequence of that routing is a standard follow-up question.
- **Treating TAO as a graph database.** TAO answers bounded, single-shard queries over a graph-shaped model. It is not a general graph engine, and saying so in an interview signals precision.
- **Ignoring the network as a resource.** At billions of small requests per second, packets per second, connection state, and switch buffers are first-class constraints. The UDP get path and incast windows exist for those reasons, and candidates who mention them show they can do the arithmetic, not just draw boxes.

---

## 12. Related Repo Content

- [Caching](../../03-hld-concepts/caching/)
- [Database Replication](../../03-hld-concepts/database-replication/)
- [Read Scaling](../../03-hld-concepts/read-scaling/)
- [Distributed Social Graph Engine (Meta TAO)](../../04-hld-projects/social-graph-engine-tao/)
- [News Feed / Timeline System](../../04-hld-projects/news-feed/)

---

## 13. Sources

- "Scaling Memcache at Facebook" (NSDI, USENIX, 2013): the memcache tier, leases, regional pools, mcsqueal invalidation, gutter servers, cold-cluster warmup, UDP gets, incast congestion control.
- "TAO: Facebook's Distributed Data Store for the Social Graph" (USENIX ATC, 2013): the object/association model, ID sharding, leader and follower cache tiers, write-through leaders, consistency model, and the billion-reads-per-second scale figure.
- Facebook engineering announcements on crossing one billion monthly active users (Facebook, 2012), for the user-scale figure.

No text is copied from these sources; the descriptions above are original explanations of the published designs. Later public write-ups cover successors and refinements (for example the mcrouter routing layer and the evolution of TAO's replication); this case study intentionally anchors on the two papers because they are the stable, citable record of the core design.

*End of Case Study*
