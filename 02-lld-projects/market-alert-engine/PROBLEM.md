# Market Alert Engine - Problem Statement

## Problem Definition
Design and implement a Stock Market & Options Alert Notification Engine. Users should be able to create alerts on stock and options based on real-time market data. The engine ingests a stream of market ticks and evaluates them against user-defined rules, notifying users when conditions are met.

## Requirements

### Capabilities
- **Real-time market tick ingestion**: Ability to process continuous streams of market data (`Tick(company, price, volume, timestamp)`).
- **Rule Engine**: Support for user-defined rules.
- **Composite Boolean Expressions**: Conditions can be combined using logical AND, OR, and NOT operations.
- **Price/Volume Threshold Monitors**: Monitor specific price levels or trading volumes (e.g., Apple > $100, Google < $40).
- **Stateful Alert Cooldown Throttling**: Prevent notification floods by suppressing alerts for the same rule/stock combination within a configured cooldown window.
- **Multi-channel Sinks**: Route triggered alerts to various notification channels (e.g., Console, Email, SMS).

### Input Format
A continuous stream of JSON-like data or object instances representing a market tick:
```json
{
  "company": "AAPL",
  "price": 134.22,
  "volume": 100,
  "timestamp": 1612134522
}
```

### Output
Triggered alerts forwarded to designated sinks.
