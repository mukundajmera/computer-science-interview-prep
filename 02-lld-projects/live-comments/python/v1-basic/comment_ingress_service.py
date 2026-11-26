import time
from typing import Dict, List, Optional, Set
from dataclasses import dataclass, field
import threading
from collections import defaultdict


@dataclass
class Comment:
    comment_id: str
    video_id: str
    user_id: str
    content: str
    timestamp: float = field(default_factory=time.time)


class CommentIngressService:
    def __init__(self, buffer_size: int = 1000, rate_limit: int = 5, window_sec: float = 1.0):
        # High-throughput comment ingestion ring buffer
        self.ring_buffer: List[Optional[Comment]] = [None] * buffer_size
        self.buffer_size = buffer_size
        self.write_index = 0
        self.lock = threading.Lock()
        
        # Sliding window rate governor: user_id -> list of timestamps
        self.user_timestamps: Dict[str, List[float]] = defaultdict(list)
        self.rate_limit = rate_limit
        self.window_sec = window_sec
        
        # Broadcast pub-sub registry: video_id -> set of subscriber_ids
        self.subscribers: Dict[str, Set[str]] = defaultdict(set)
        # subscriber_id -> list of comments
        self.subscriber_queues: Dict[str, List[Comment]] = defaultdict(list)

    def subscribe(self, subscriber_id: str, video_id: str):
        with self.lock:
            self.subscribers[video_id].add(subscriber_id)

    def unsubscribe(self, subscriber_id: str, video_id: str):
        with self.lock:
            if subscriber_id in self.subscribers[video_id]:
                self.subscribers[video_id].remove(subscriber_id)

    def is_rate_limited(self, user_id: str, current_time: float) -> bool:
        timestamps = self.user_timestamps[user_id]
        # Remove timestamps outside the sliding window
        while timestamps and current_time - timestamps[0] > self.window_sec:
            timestamps.pop(0)
            
        if len(timestamps) >= self.rate_limit:
            return True
            
        timestamps.append(current_time)
        return False

    def publish_comment(self, video_id: str, user_id: str, content: str) -> Optional[str]:
        current_time = time.time()
        
        with self.lock:
            if self.is_rate_limited(user_id, current_time):
                return None
                
            comment_id = f"c_{current_time}_{user_id}"
            comment = Comment(comment_id, video_id, user_id, content, current_time)
            
            # Write to ring buffer
            self.ring_buffer[self.write_index] = comment
            self.write_index = (self.write_index + 1) % self.buffer_size
            
            # Broadcast to subscribers
            for sub_id in self.subscribers[video_id]:
                self.subscriber_queues[sub_id].append(comment)
                
            return comment_id

    def get_comments(self, subscriber_id: str) -> List[Comment]:
        with self.lock:
            comments = self.subscriber_queues[subscriber_id]
            self.subscriber_queues[subscriber_id] = []
            return comments

