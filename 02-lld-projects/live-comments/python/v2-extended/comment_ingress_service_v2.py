from typing import Optional, List, Protocol
try:
    from .comment_fanout_service import CommentFanoutService
    from .live_session_registry import LiveSessionRegistry
    from .comment_replay_store import CommentReplayStore
except ImportError:
    from comment_fanout_service import CommentFanoutService
    from live_session_registry import LiveSessionRegistry
    from comment_replay_store import CommentReplayStore


class ModerationPipeline(Protocol):
    def is_approved(self, payload: str) -> bool: ...


class CommentIngressServiceV2:
    def __init__(self,
                 fanout_service: CommentFanoutService,
                 session_registry: LiveSessionRegistry,
                 replay_store: CommentReplayStore,
                 moderation_pipeline: ModerationPipeline) -> None:
        self.fanout_service = fanout_service
        self.session_registry = session_registry
        self.replay_store = replay_store
        self.moderation_pipeline = moderation_pipeline

    def publish_comment(self, stream_id: str, user_id: str, payload: str, event_time_ms: int) -> None:
        if not self.moderation_pipeline.is_approved(payload):
            return

        self.fanout_service.fanout(stream_id, payload, event_time_ms)
        
        # If the replay store supports adding, add it.
        # In a real app we might have a separate worker doing this, or the same interface.
        if hasattr(self.replay_store, "add_comment"):
            self.replay_store.add_comment(stream_id, payload) # type: ignore

    def join_stream(self, stream_id: str, session_id: str, user_id: str) -> List[str]:
        self.session_registry.register(stream_id, session_id, user_id)
        return self.replay_store.replay(stream_id, "", 50)
        
    def leave_stream(self, stream_id: str, session_id: str) -> None:
        self.session_registry.unregister(stream_id, session_id)
