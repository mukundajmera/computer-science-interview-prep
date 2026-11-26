# Content Moderation Platform — Comparison

## vs Bot Detection Platform

| Aspect | Content Moderation | Bot Detection |
|---|---|---|
| Unit of decision | content item | account/session |
| Core signals | text/media/context | behavior/graph/device |
| Main actions | allow/demote/review/remove | allow/limit/challenge/suspend |

## vs Video Streaming

| Aspect | Content Moderation | Video Streaming |
|---|---|---|
| Main risk | policy/safety mistakes | playback/ingest latency |
| Hot path | inference + policy decision | segment delivery via CDN |
| Human loop | reviewer workflow | mostly SRE/content ops |
