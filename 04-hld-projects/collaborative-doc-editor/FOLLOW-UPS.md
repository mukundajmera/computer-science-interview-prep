# Collaborative Document Editor — Follow-Up Questions

## 1. How do we scale to millions of websocket connections?
Use regional websocket gateways, session sharding by document ID, and connection fanout isolation.

## 2. How do we support >100 viewers on a hot document?
Split active editor and passive viewer channels; preserve writer constraints.

## 3. How do we add full document version history?
Persist periodic immutable snapshots plus retained operation windows for replay.

## 4. What changes for offline editing?
Queue local ops with causal metadata and reconcile on reconnect.

## 5. How do we reduce memory cost for session state?
Keep active session metadata in memory and expire stale presence aggressively.

## 6. How do we tolerate node loss mid-session?
Use reconnect with replay token and deterministic document-to-node rerouting.
