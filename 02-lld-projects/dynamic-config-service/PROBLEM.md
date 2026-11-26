# Problem: Dynamic Feature Flag Engine

## Description
Design and implement a dynamic configuration and feature flag engine that can evaluate feature flags based on user attributes, apply percentage-based rollouts, handle change listeners, and provide sensible fallbacks. The system must support multi-variant flags (not just booleans).

## Requirements

1. **Multi-variant Flags**: A flag can evaluate to a boolean, string, or integer value.
2. **Segment Evaluation**: Flags can define targeting rules based on user attributes (e.g., `country == "US"`, `is_beta_user == true`).
3. **Percentage Rollouts**: Flags can have rollout percentages (e.g., 20% of users get variant A, 80% get variant B) which must be consistent per user.
4. **Change Listeners**: Components can register to be notified when a flag configuration changes.
5. **Fallback Defaults**: If evaluation fails or no rule matches, a default value must be returned.

## Use Cases
- A backend service dynamically enabling a new feature for only 10% of users in the "EU" segment.
- A mobile app receiving configuration for theme colors based on subscription tier.
- A server subscribing to configuration updates to re-initialize an internal component without restarting.

## Versioned Implementation Scope

- **v1-basic**: Basic single-variant feature flags with a deterministic explicit hashing algorithm (e.g., MD5 with UTF-8 byte encoding) for basic user percentage rollouts. Atomic immutable config snapshots.
- **v2-extended**: Adds multi-variant flags, attribute-based segment targeting rules, change listeners, and robust fallback handling for missing flags or invalid percentages. Handles stale updates properly.
- **v3-optimized**: Optimizes evaluation performance with compiled rule engines, adds support for version rollback, and explicit tenant override precedence handling.
