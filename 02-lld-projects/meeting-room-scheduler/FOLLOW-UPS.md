# Meeting Room Scheduler - Follow-Up Questions

## Follow-up questions
1. **Recurring Meetings**: How would you support daily/weekly recurring meetings?
   - *Approach*: Implement RRULE (RFC 5545). Expand recurring instances dynamically or generate them up to a time horizon (e.g., 1 year) to detect conflicts early.

2. **Multi-Room Video Conferencing**: How to book linked rooms across different offices simultaneously?
   - *Approach*: Requires distributed transactions or two-phase commit (2PC) logic. If one room fails to book, roll back the other rooms.

3. **Auto-Release on No-Show**: If attendees do not check in within 10 minutes, release the room.
   - *Approach*: A background scheduler or delay queue (e.g., Redis expiring keys or a PriorityQueue) that checks the room's sensor status.

4. **Room Cleaning Buffer Time**: Require a 15-minute buffer after meetings for cleaning.
   - *Approach*: When booking `[start, end)`, artificially extend the blocked interval in the room's calendar to `[start, end + 15m)`.

## Interviewer probes to prepare
- "How does your system perform if there are 10,000 rooms and users book frequently?"
- "What if we have cross-region latency?"
