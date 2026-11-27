# HLD Diagram Source Matrix

This matrix tracks whether each HLD project has auditable Mermaid source files. Mermaid `.mmd` files are the committed source of truth; rendered SVG/PNG outputs should stay out of the repository unless an explicit export task requests them.

## Classification Legend

| Classification | Meaning |
|---|---|
| `external .mmd` | The project has one or more Mermaid sources under `diagrams/`. Inline diagrams may still need later deduplication. |
| `inline-only with rationale` | The project currently keeps Mermaid only inside Markdown; follow-up should extract reusable sources when the diagram is part of the durable design. |
| `missing source` | No project-local `.mmd` file and no inline Mermaid block were found; the project needs a diagram decision. |
| `verified no diagram needed` | The project was reviewed and intentionally does not need a diagram source for its current scope. |

## Project Inventory

| Project | Primary docs | Inline Mermaid blocks | External .mmd sources | Classification | Required follow-up | Notes |
|---|---|---:|---:|---|---|---|
| [API Gateway](./api-gateway/) | [DESIGN.md](./api-gateway/DESIGN.md) | 1 | 1 | `external .mmd` | Keep source synchronized with design text. | Architecture source exists. |
| [Ad Click Aggregator](./ad-click-aggregator/) | [DESIGN.md](./ad-click-aggregator/DESIGN.md) | 1 | 1 | `external .mmd` | Keep source synchronized with design text. | Architecture source exists. |
| [Bot Detection](./bot-detection/) | [DESIGN.md](./bot-detection/DESIGN.md) | 1 | 1 | `external .mmd` | Keep source synchronized with design text. | Architecture source exists. |
| [Bot Detection Platform](./bot-detection-platform/) | [DESIGN.md](./bot-detection-platform/DESIGN.md) | 1 | 0 | `inline-only with rationale` | Extract architecture diagram when this project is next edited. | Advanced variant currently embeds the diagram. |
| [Brokerage Platform](./brokerage-platform/) | [DESIGN.md](./brokerage-platform/DESIGN.md) | 1 | 3 | `external .mmd` | Reconcile inline architecture with external sources. | Existing sources cover architecture, sequence, and database views. |
| [Chat Service](./chat-service/) | [DESIGN.md](./chat-service/DESIGN.md) | 5 | 3 | `external .mmd` | Reconcile inline flows with external sources. | Multiple inline flows remain in the design doc. |
| [Collaborative Doc Editor](./collaborative-doc-editor/) | [DESIGN.md](./collaborative-doc-editor/DESIGN.md) | 1 | 3 | `external .mmd` | Reconcile inline architecture with external sources. | Existing sources cover architecture, sequence, and database views. |
| [Content Delivery Network](./content-delivery-network/) | [DESIGN.md](./content-delivery-network/DESIGN.md) | 0 | 1 | `external .mmd` | Keep source synchronized with design text. | Architecture source exists. |
| [Content Moderation](./content-moderation/) | [DESIGN.md](./content-moderation/DESIGN.md) | 1 | 1 | `external .mmd` | Keep source synchronized with design text. | Baseline moderation source exists. |
| [Content Moderation Platform](./content-moderation-platform/) | [DESIGN.md](./content-moderation-platform/DESIGN.md) | 1 | 0 | `inline-only with rationale` | Extract architecture diagram when this project is next edited. | Advanced variant currently embeds the diagram. |
| [Digital Wallet](./digital-wallet/) | [DESIGN.md](./digital-wallet/DESIGN.md) | 0 | 1 | `external .mmd` | Keep source synchronized with design text. | Architecture source exists. |
| [Distributed Cache](./distributed-cache/) | [DESIGN.md](./distributed-cache/DESIGN.md) | 1 | 3 | `external .mmd` | Reconcile inline architecture with external sources. | Existing sources cover architecture, sequence, and database views. |
| [Distributed Cloud Storage S3](./distributed-cloud-storage-s3/) | [DESIGN.md](./distributed-cloud-storage-s3/DESIGN.md) | 0 | 0 | `missing source` | Needs diagram decision. | New project. |
| [Distributed Object Storage](./distributed-object-storage/) | [DESIGN.md](./distributed-object-storage/DESIGN.md) | 0 | 1 | `external .mmd` | Keep source synchronized with design text. | Architecture source exists. |
| [Distributed Social Graph Engine](./social-graph-engine-tao/) | [DESIGN.md](./social-graph-engine-tao/DESIGN.md) | 0 | 1 | `external .mmd` | Keep source synchronized with design text. | Architecture source exists. |
| [Distributed Tracing](./distributed-tracing/) | [DESIGN.md](./distributed-tracing/DESIGN.md) | 1 | 0 | `inline-only with rationale` | Extract architecture diagram when this project is next edited. | Inline architecture diagram included in DESIGN.md. |
| [Distributed Unique ID Generator (Snowflake)](./distributed-unique-id-snowflake/) | [DESIGN.md](./distributed-unique-id-snowflake/DESIGN.md) | 0 | 1 | `external .mmd` | Keep source synchronized with design text. | Architecture source exists. |
| [Distributed Workflow Orchestrator](./distributed-workflow-orchestrator/) | [DESIGN.md](./distributed-workflow-orchestrator/DESIGN.md) | 0 | 1 | `external .mmd` | Keep source synchronized with design text. | Architecture source exists. |
| [E-commerce Backend](./ecommerce-backend/) | [DESIGN.md](./ecommerce-backend/DESIGN.md) | 9 | 3 | `external .mmd` | Reconcile inline architecture, checkout, and data-flow diagrams with external sources. | Highest inline duplication in this audit pass. |
| [File Storage](./file-storage/) | [DESIGN.md](./file-storage/DESIGN.md) | 5 | 3 | `external .mmd` | Reconcile inline flows with external sources. | Existing sources cover architecture, sequence, and database views. |
| [Google Maps & Navigation](./google-maps/) | [DESIGN.md](./google-maps/DESIGN.md) | 0 | 2 | `external .mmd` | Keep source synchronized with design text. | Existing sources cover architecture, sequence, and database views. |
| [HLD Design Template: Distributed Email Service (Gmail)](./distributed-email-service/) | [DESIGN.md](./distributed-email-service/DESIGN.md) | 0 | 1 | `external .mmd` | Keep source synchronized with design text. | Architecture source exists. |
| [HLD Design: Nearby Friends](./nearby-friends/) | [DESIGN.md](./nearby-friends/DESIGN.md) | 0 | 2 | `external .mmd` | Keep source synchronized with design text. | Existing sources cover architecture, sequence, and database views. |
| [Job Scheduler](./job-scheduler/) | [DESIGN.md](./job-scheduler/DESIGN.md) | 0 | 1 | `external .mmd` | Keep source synchronized with design text. | Architecture source exists. |
| [Kafka Distributed Broker](./kafka-distributed-broker/) | [DESIGN.md](./kafka-distributed-broker/DESIGN.md) | 0 | 2 | `external .mmd` | Keep source synchronized with design text. | Architecture and replication sources exist. |
| [Live Comments](./live-comments/) | [DESIGN.md](./live-comments/DESIGN.md) | 1 | 0 | `inline-only with rationale` | Extract architecture diagram when this project is next edited. | Inline real-time path is reusable. |
| [Live Video Streaming Pipeline](./live-video-streaming-pipeline/) | [DESIGN.md](./live-video-streaming-pipeline/DESIGN.md) | 0 | 1 | `external .mmd` | Keep source synchronized with design text. | Architecture source exists. |
| [Metrics Monitoring](./metrics-monitoring/) | [DESIGN.md](./metrics-monitoring/DESIGN.md) | 0 | 1 | `external .mmd` | Keep source synchronized with design text. | Architecture source exists for the baseline observability project. |
| [Multi-Region Active-Active — Design](./multi-region-active-active/) | [DESIGN.md](./multi-region-active-active/DESIGN.md) | 0 | 1 | `external .mmd` | Keep source synchronized with design text. | Architecture source exists. |
| [News Feed](./news-feed/) | [DESIGN.md](./news-feed/DESIGN.md) | 5 | 3 | `external .mmd` | Reconcile inline flows with external sources. | Existing sources cover architecture, sequence, and database views. |
| [Notification Service](./notification-service/) | [DESIGN.md](./notification-service/DESIGN.md) | 4 | 3 | `external .mmd` | Reconcile inline notification and retry flows with external sources. | Design doc already links to `diagrams/`. |
| [Online Auction](./online-auction/) | [DESIGN.md](./online-auction/DESIGN.md) | 1 | 0 | `inline-only with rationale` | Extract architecture diagram when this project is next edited. | Inline bidding path should become reusable source. |
| [Pastebin Design](./pastebin/) | [DESIGN.md](./pastebin/DESIGN.md) | 0 | 1 | `external .mmd` | Keep source synchronized with design text. | Architecture source exists. |
| [Payment System](./payment-system/) | [DESIGN.md](./payment-system/DESIGN.md) | 0 | 1 | `external .mmd` | Keep source synchronized with design text. | Architecture source exists. |
| [Price Tracking Service](./price-tracking-service/) | [DESIGN.md](./price-tracking-service/DESIGN.md) | 1 | 0 | `inline-only with rationale` | Extract architecture diagram when this project is next edited. | Inline polling/event flow is reusable. |
| [Proximity Service](./proximity-service-yelp/) | [DESIGN.md](./proximity-service-yelp/DESIGN.md) | 0 | 1 | `external .mmd` | Keep source synchronized with design text. | Architecture source exists. |
| [Quick Commerce Delivery](./quick-commerce-delivery/) | [DESIGN.md](./quick-commerce-delivery/DESIGN.md) | 1 | 1 | `external .mmd` | Reconcile inline architecture with the extracted source during a later diagram cleanup. | First representative extraction: [architecture.mmd](./quick-commerce-delivery/diagrams/architecture.mmd). |
| [Real-Time Gaming Leaderboard](./realtime-gaming-leaderboard/) | [DESIGN.md](./realtime-gaming-leaderboard/DESIGN.md) | 0 | 1 | `external .mmd` | Keep source synchronized with design text. | Architecture source exists. |
| [Realtime Metrics Platform](./realtime-metrics-platform/) | [DESIGN.md](./realtime-metrics-platform/DESIGN.md) | 0 | 1 | `external .mmd` | Keep source synchronized with design text. | Architecture source exists for the advanced observability project. |
| [Ride Sharing](./ride-sharing/) | [DESIGN.md](./ride-sharing/DESIGN.md) | 1 | 3 | `external .mmd` | Reconcile inline architecture with external sources. | Existing sources cover architecture, sequence, and database views. |
| [Search Autocomplete](./search-autocomplete/) | [DESIGN.md](./search-autocomplete/DESIGN.md) | 0 | 2 | `external .mmd` | Keep source synchronized with design text. | Architecture and sequence sources exist. |
| [Social Post Search](./social-post-search/) | [DESIGN.md](./social-post-search/DESIGN.md) | 1 | 0 | `inline-only with rationale` | Extract architecture diagram when this project is next edited. | Inline indexing/search flow is reusable. |
| [Stock Exchange Matching Engine](./stock-exchange-matching-engine/) | [DESIGN.md](./stock-exchange-matching-engine/DESIGN.md) | 0 | 2 | `external .mmd` | Keep source synchronized with design text. | Architecture and sequence sources exist. |
| [Ticketing Platform](./ticketing-platform/) | [DESIGN.md](./ticketing-platform/DESIGN.md) | 1 | 0 | `inline-only with rationale` | Extract architecture diagram when this project is next edited. | Inline seat-hold flow is reusable. |
| [URL Shortener](./url-shortener/) | [DESIGN.md](./url-shortener/DESIGN.md) | 4 | 3 | `external .mmd` | Reconcile inline architecture, write path, and data diagrams with external sources. | Design doc already links to `diagrams/`. |
| [Video Recommendations](./video-recommendations/) | [DESIGN.md](./video-recommendations/DESIGN.md) | 0 | 1 | `external .mmd` | Keep source synchronized with design text. | Architecture source exists. |
| [Video Streaming](./video-streaming/) | [DESIGN.md](./video-streaming/DESIGN.md) | 1 | 3 | `external .mmd` | Reconcile inline architecture with external sources. | Existing sources cover architecture, sequence, and database views. |
| [Web Crawler](./web-crawler/) | [DESIGN.md](./web-crawler/DESIGN.md) | 0 | 1 | `external .mmd` | Keep source synchronized with design text. | Architecture source exists. |

## Current Summary

| Status | Count | Projects |
|---|---:|---|
| `external .mmd` | 39 | API Gateway, Ad Click Aggregator, Bot Detection, Brokerage Platform, Chat Service, Collaborative Doc Editor, Content Delivery Network, Content Moderation, Digital Wallet, Distributed Cache, Distributed Object Storage, Distributed Social Graph Engine, Distributed Unique ID Generator (Snowflake), Distributed Workflow Orchestrator, E-commerce Backend, File Storage, Google Maps & Navigation, HLD Design Template: Distributed Email Service (Gmail), HLD Design: Nearby Friends, Job Scheduler, Kafka Distributed Broker, Live Video Streaming Pipeline, Metrics Monitoring, Multi-Region Active-Active — Design, News Feed, Notification Service, Pastebin Design, Payment System, Proximity Service, Quick Commerce Delivery, Real-Time Gaming Leaderboard, Realtime Metrics Platform, Ride Sharing, Search Autocomplete, Stock Exchange Matching Engine, URL Shortener, Video Recommendations, Video Streaming, Web Crawler |
| `inline-only with rationale` | 8 | Bot Detection Platform, Content Moderation Platform, Distributed Tracing, Live Comments, Online Auction, Price Tracking Service, Social Post Search, Ticketing Platform |
| `missing source` | 1 | Distributed Cloud Storage S3 |
| `verified no diagram needed` | 0 | None yet. |

## Validation Notes

- Re-run `rg --files 04-hld-projects -g '*.mmd'` after adding or moving diagram sources.
- Re-run `rg -n '```mermaid' 04-hld-projects/*/*.md` after extracting inline blocks from project Markdown docs.
- If Mermaid CLI is installed, render changed sources to `/tmp`; do not commit rendered outputs by default.
