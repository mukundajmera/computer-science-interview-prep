import threading
import time
from typing import Dict, List, Optional
import collections

class LiveStreamIngestServer:
    def __init__(self):
        self.active_sessions: Dict[str, float] = {}
        self.lock = threading.Lock()

    def start_session(self, stream_id: str) -> bool:
        with self.lock:
            if stream_id in self.active_sessions:
                return False
            self.active_sessions[stream_id] = time.time()
            return True

    def end_session(self, stream_id: str) -> bool:
        with self.lock:
            if stream_id in self.active_sessions:
                del self.active_sessions[stream_id]
                return True
            return False

    def is_active(self, stream_id: str) -> bool:
        with self.lock:
            return stream_id in self.active_sessions

class AbrTranscoderLadder:
    def __init__(self):
        self.renditions = ["1080p", "720p", "480p", "360p"]

    def transcode_segment(self, stream_id: str, segment_id: int) -> Dict[str, str]:
        # Simulates generating multiple renditions for a single segment
        return {
            rendition: f"{stream_id}_{rendition}_seg_{segment_id}.ts"
            for rendition in self.renditions
        }

class LiveManifestManager:
    def __init__(self, window_size: int = 5):
        self.window_size = window_size
        self.manifests: Dict[str, collections.deque] = {}
        self.lock = threading.Lock()

    def append_segment(self, stream_id: str, rendition: str, segment_url: str):
        with self.lock:
            if stream_id not in self.manifests:
                self.manifests[stream_id] = collections.deque(maxlen=self.window_size)
            
            # Simple simulation: just keeping a list of recent segments
            self.manifests[stream_id].append({"rendition": rendition, "url": segment_url})

    def get_manifest(self, stream_id: str) -> List[Dict[str, str]]:
        with self.lock:
            if stream_id in self.manifests:
                return list(self.manifests[stream_id])
            return []

class OriginShieldTree:
    def __init__(self):
        self.l1_cache: Dict[str, str] = {}
        self.l2_cache: Dict[str, str] = {}
        self.origin: Dict[str, str] = {}
        self.lock = threading.Lock()

    def write_to_origin(self, key: str, value: str):
        with self.lock:
            self.origin[key] = value

    def fetch(self, key: str) -> Optional[str]:
        with self.lock:
            if key in self.l1_cache:
                return self.l1_cache[key]
            if key in self.l2_cache:
                self.l1_cache[key] = self.l2_cache[key]
                return self.l2_cache[key]
            if key in self.origin:
                val = self.origin[key]
                self.l2_cache[key] = val
                self.l1_cache[key] = val
                return val
            return None
