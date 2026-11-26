# Video Streaming — Common Interview Pitfalls

1. Ignoring resumable upload state and idempotent completion.
2. Treating playback as direct file download (no manifest/segment model).
3. No async transcode pipeline between upload and ready state.
4. Omitting CDN strategy and origin protection controls.
5. Recommendation design as single-stage heavy model only.
6. No cold-start handling for new users/videos.
7. Missing feedback-loop safeguards (popularity lock-in).
8. No explicit latency budget split across recommendation stages.
9. No graceful degradation path when heavy ranker is slow/unavailable.
