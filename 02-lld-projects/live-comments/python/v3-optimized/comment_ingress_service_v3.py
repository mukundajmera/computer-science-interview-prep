from typing import List, Protocol

class IdempotencyStore(Protocol):
    def claim(self, key: str, ttl_ms: int) -> bool: ...

class DistributedCommentStore(Protocol):
    def append_comment(self, stream_id: str, comment_payload: str, region: str) -> None: ...
    def get_recent_comments(self, stream_id: str, region: str, limit: int) -> List[str]: ...

class DistributedSessionRegistry(Protocol):
    def register_session(self, stream_id: str, session_id: str, user_id: str, region: str) -> None: ...
    def unregister_session(self, stream_id: str, session_id: str, region: str) -> None: ...

class DistributedFanoutService(Protocol):
    def broadcast(self, stream_id: str, comment_payload: str, region: str) -> None: ...

class ModerationPipelineV3(Protocol):
    def is_approved(self, payload: str) -> bool: ...

class CommentIngressServiceV3:
    def __init__(self, 
                 comment_store: DistributedCommentStore, 
                 idempotency_store: IdempotencyStore,
                 fanout_service: DistributedFanoutService,
                 session_registry: DistributedSessionRegistry,
                 moderation_pipeline: ModerationPipelineV3) -> None:
        self.comment_store = comment_store
        self.idempotency_store = idempotency_store
        self.fanout_service = fanout_service
        self.session_registry = session_registry
        self.moderation_pipeline = moderation_pipeline

    def publish_comment(self, stream_id: str, payload: str, idempotency_key: str, region: str) -> bool:
        if not self.idempotency_store.claim(idempotency_key, 60_000):
            return False
            
        if not self.moderation_pipeline.is_approved(payload):
            return False

        self.comment_store.append_comment(stream_id, payload, region)
        self.fanout_service.broadcast(stream_id, payload, region)
        return True

    def join_stream(self, stream_id: str, session_id: str, user_id: str, region: str) -> List[str]:
        self.session_registry.register_session(stream_id, session_id, user_id, region)
        return self.comment_store.get_recent_comments(stream_id, region, 50)

    def leave_stream(self, stream_id: str, session_id: str, region: str) -> None:
        self.session_registry.unregister_session(stream_id, session_id, region)
