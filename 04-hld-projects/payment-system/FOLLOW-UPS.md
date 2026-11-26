# Payment System — Follow-Up Questions

## 1. How do you support partial capture and multiple captures per authorization?

Model `authorization_amount`, `captured_amount`, and one or more `capture` transactions under the same payment intent. The state remains `authorized` or `partially_captured` until captured amount reaches the authorization limit or the authorization expires.

## 2. What architecture changes are needed for multi-currency and FX conversion?

Add an FX quote service that records quote id, rate, source currency, target currency, expiry, and rounding rule. Store the original amount, settlement amount, and accounting amount separately so refunds and disputes can replay the same conversion basis.

## 3. How would you model chargeback/dispute workflows and evidence retention?

Create a `dispute` aggregate linked to payment intent, transaction, merchant, evidence bundle, deadline, and provider case id. Retain signed evidence and webhook history for the required dispute window, and keep dispute state separate from payment capture state.

## 4. How do you roll out a new payment gateway with safe traffic shifting?

Use a gateway router with merchant/region/card-bin rules, shadow authorization where legally safe, percentage rollout, per-gateway circuit breakers, and instant rollback to the previous adapter. Compare approval rate, timeout rate, hard-decline mix, and reconciliation mismatches before increasing traffic.

## 5. Which controls enforce PCI scope minimization in this architecture?

Use gateway-hosted fields or tokenized payment methods, never store PAN/CVV in core services, isolate gateway adapters, redact logs, and keep audit trails around token use rather than raw card data.

## Follow-up scoring signals

Strong answers preserve the core state machine and idempotency rules while adding the extension. Weak answers bolt on side services without explaining how they affect settlement, reconciliation, rollback, or audit evidence.
