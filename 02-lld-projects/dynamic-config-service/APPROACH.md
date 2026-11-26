# Approach: Dynamic Feature Flag Engine

## Overview

The Dynamic Configuration Service evaluates feature flags efficiently and safely, using rules, segments, and deterministic hashing for rollouts.

### Core Entities

- **UserContext**: The attributes identifying the user (ID, attributes map).
- **FeatureFlag**: Contains the flag's rules, variants, rollout configurations, and fallback values.
- **Rule**: A condition that evaluates a UserContext (e.g., equality, in-list).
- **ConfigEngine**: The primary entry point for evaluating flags and managing configurations.
- **ConfigObserver/Listener**: Interface for clients to listen to updates to a flag.

### Evaluation Logic

1. **Rule Evaluation**: We evaluate targeting rules top-to-bottom. The first rule to match applies.
2. **Rollout Logic**: If a rule specifies a rollout, we hash the `UserId + FlagKey` using a deterministic cross-language hash with fixed byte encoding (e.g., MD5 of UTF-8 encoded string) to get a deterministic integer (0-100). We then map this integer to a variant based on configured percentages. No built-in randomized hash is allowed to ensure same tenant/user rollout cohort in both Java and Python languages.
3. **Fallback**: If no rules match or there is an error (e.g., missing flag, invalid percentage), the engine returns the default variant.

### Concurrency and Updates

- Updates to flags must be thread-safe.
- We use **atomic immutable config snapshots** to ensure safe concurrent evaluations without unnecessary blocking. Version rollbacks and stale updates must be explicitly handled by comparing versions on update.
- Tenant override precedence takes priority over normal percentage rules.
