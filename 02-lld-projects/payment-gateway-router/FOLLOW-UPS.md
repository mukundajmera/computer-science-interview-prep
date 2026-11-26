# Payment Gateway Router - Follow-Up Questions

## Follow-up questions

1. **How would you implement distributed two-phase commit with external banks?**
   - Typically impossible since external APIs don't support 2PC locks. Instead, we use asynchronous reconciliation and compensation (Sagas) rather than distributed locks.

2. **How would you implement smart dynamic fee routing?**
   - We could extend `RoutingStrategy` to query a bin-lookup service to determine the issuer card type and route transactions to the provider offering the lowest fee for that card.

3. **How do we handle discrepancies between our system and the bank?**
   - Asynchronous reconciliation batch jobs against bank settlement files. Every day, ingest the settlement file, match transaction IDs, and alert on mismatches (missing funds, unrecorded payments).

## Variants and extensions
- **Webhook Deduplication**: Handling duplicated webhooks sent by Stripe. This shares the same idempotency store logic but operates asynchronously to update transaction statuses.

## Interviewer probes to prepare
- "What if the request to Stripe times out? How do you know if the user was charged or not before failing over to Razorpay?"
- "How large will the sliding window for success rates get in memory?"
