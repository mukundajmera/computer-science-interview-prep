# Problem: Dynamic Configuration & Feature Flag Service

## Overview
Design and implement an in-memory Dynamic Configuration and Feature Flag Service. A Feature Flag service allows developers to enable, disable, or modify features in a live application without deploying new code. This is critical for A/B testing, gradual rollouts, and kill switches.

## Requirements

### 1. Feature Flag Evaluation
The service must support evaluating feature flags based on a given user context (e.g., `userId`, `country`, `appVersion`).
* **Boolean Flags:** Simple ON/OFF toggles.
* **Targeting/Allowlist Flags:** Enable a feature only for specific user IDs or groups.
* **Percentage/Gradual Rollout Flags:** Enable a feature for a deterministic percentage of users (e.g., 20% of users). The evaluation must be consistent for the same user.
* **Rule-based Flags:** Complex rules combining multiple conditions (e.g., `country == 'US'` AND `appVersion >= '2.0.0'`).

### 2. Dynamic Updates
The system must be able to receive configuration updates dynamically at runtime. When a flag's configuration changes (e.g., a flag is turned off, or a rollout percentage increases), the service should update its internal state and evaluate subsequent requests using the new configuration. Clients should be notified of changes if they are actively listening (Observer pattern).

### 3. Concurrency
The service will be accessed by multiple threads simultaneously. Flag evaluations and configuration updates must be thread-safe. Evaluations should be highly performant and non-blocking, prioritizing read throughput.

### 4. Default Values
If a flag is not found, or if an evaluation fails due to missing context attributes, the service must return a predefined default value or fallback value provided by the caller.

## Expected Patterns
* **Singleton:** The Configuration Manager should be a single instance across the application.
* **Strategy:** Different flag evaluation logic (Boolean, Percentage, Rule-based) should be implemented using the Strategy pattern.
* **Observer:** Notify subscribed components when a specific flag changes.
* **Rule Engine:** Evaluate complex conditions dynamically based on user context.
