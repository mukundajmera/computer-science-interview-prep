# Distributed Workflow Orchestrator - Comparison

## Overview

When designing a system to manage long-running distributed processes, developers typically choose between three main paradigms: choreography (event-driven), centralized state machines (JSON/YAML defined), and code-based orchestration (Temporal/Cadence).

## Paradigm Comparison

| Concern | Choreography (Event-Driven) | Centralized State Machine (AWS Step Functions) | Code-Based Orchestrator (Temporal) |
| :--- | :--- | :--- | :--- |
| **Logic Definition** | Implicit; distributed across many services via pub/sub. | Explicit JSON/YAML declarative definitions. | Explicit; written in general-purpose languages (Java/Go). |
| **State Storage** | None (or decentralized in individual services). | Orchestrator internal database. | Orchestrator internal database (Event Sourcing). |
| **Observability** | Difficult; requires distributed tracing to piece together the flow. | Excellent visual dashboards. | Excellent; explicit event histories and queryable state. |
| **Testing** | Hard; requires standing up multiple services. | Medium; requires mocking the orchestrator engine. | Easy; standard unit testing frameworks against a local test environment. |
| **Flexibility** | High; services are loosely coupled. | Low; limited by the declarative language features. | High; full power of a Turing-complete language. |

## Storage Approaches for Code-Based Orchestration

If building a code-based orchestrator, how do you save the state of a workflow that might run for months?

| Feature | Event Sourcing (Replay) | JVM/Process Checkpointing |
| :--- | :--- | :--- |
| **Mechanism** | Save every API call input/output to a database. Re-run code to rebuild state. | Serialize the entire memory heap and call stack to a BLOB and save it. |
| **Portability** | High. State is just data. A workflow started in Python could theoretically be resumed in Java. | Very Low. Dependent on language versions, OS, and memory layouts. |
| **Upgrades** | Medium complexity. Requires versioning the code paths if logic changes to avoid breaking replay. | Hard. If a class definition changes, deserializing the old memory snapshot fails. |
| **Performance** | High throughput (appending small events), but replay takes CPU time. | High I/O cost (saving megabytes of heap constantly), but resume is instantaneous. |
| **Decision** | **Chosen.** Standard for modern orchestrators (Temporal, Cadence). | Rejected. Too fragile for generic multi-language support. |

## Cross-Links
- [Approach](APPROACH.md)
- [Design Document](DESIGN.md)
