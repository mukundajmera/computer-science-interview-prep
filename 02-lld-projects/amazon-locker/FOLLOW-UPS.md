# Amazon Locker — Follow-Up Questions

## 1. How to allow size fallback?
Use policy-based selection with ordered size escalation.

## 2. How to handle broken compartments?
Introduce explicit compartment status and skip non-serviceable states.

## 3. How to guarantee physical deposit happened?
Split reserve and confirm operations; issue token only on confirm.

## 4. How to support many locker stations?
Introduce station-level routing and station-local allocation policy.

## 5. How to add failed-attempt lockout?
Track token attempt counts with bounded retry policy.
