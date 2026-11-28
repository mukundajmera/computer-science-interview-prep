"""
v2-extended live video streaming pipeline.

Improvements over v1-basic (each has dedicated tests):

1. Flash-crowd request collapsing with bounded cache tiers and origin
   metrics (FOLLOW-UPS.md #2, PITFALLS.md #2): OriginShieldTree collapses
   concurrent misses for the same segment into a single origin load
   (singleflight), bounds each cache tier with LRU eviction so a raid
   cannot grow them without limit, and counts origin reads so the load
   on the origin is observable.

2. Transcoder node failure recovery with time-aligned keyframes
   (FOLLOW-UPS.md #1, PITFALLS.md #4): AbrTranscoderLadder runs each
   rendition on a transcode node, reassigns work to a live node when one
   dies mid-stream (raising loudly if none remain), and stamps every
   rendition of a segment with the same aligned keyframe timestamp so a
   player switching renditions never hits an unaligned IDR boundary.

3. Live-to-VOD archival (FOLLOW-UPS.md #4): LiveManifestManager keeps
   the complete segment history alongside the sliding live window and
   turns a finished stream into a permanent VOD playlist.
"""

import collections
import threading
import time
from typing import Callable, Dict, List, Optional


class LiveStreamIngestServer:
    """Parity with v1: thread-safe session tracking."""

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
    """v1 parity plus node failover (improvement #2)."""

    def __init__(self, nodes: Optional[List[str]] = None):
        self.renditions = ["1080p", "720p", "480p", "360p"]
        self.nodes: List[str] = list(nodes) if nodes else ["gpu-1"]
        self.dead_nodes = set()
        self._lock = threading.Lock()

    def fail_node(self, node_id: str):
        """Failure injection: mark a transcode node dead."""
        with self._lock:
            self.dead_nodes.add(node_id)

    def revive_node(self, node_id: str):
        with self._lock:
            self.dead_nodes.discard(node_id)

    def transcode_segment(self, stream_id: str, segment_id: int) -> Dict[str, str]:
        # v1-compatible signature and output: rendition -> segment URL.
        return {
            rendition: f"{stream_id}_{rendition}_seg_{segment_id}.ts"
            for rendition in self.renditions
        }

    def transcode_segment_resilient(
        self,
        stream_id: str,
        segment_id: int,
        keyframe_interval_seconds: float = 2.0,
    ) -> Dict[str, Dict[str, object]]:
        """Transcode on live nodes with failover and aligned keyframes.

        Each rendition is assigned to a live node; dead nodes are skipped
        so a dead GPU node never drops the stream (FOLLOW-UPS.md #1).
        Every rendition carries the same keyframe timestamp, aligned down
        to the keyframe interval, so ABR switches are seamless
        (PITFALLS.md #4).
        """
        with self._lock:
            live_nodes = [n for n in self.nodes if n not in self.dead_nodes]
        if not live_nodes:
            raise RuntimeError("NoLiveTranscodeNodes: all transcode nodes are down")

        # Same aligned IDR boundary for every rendition of this segment.
        segment_time = segment_id * keyframe_interval_seconds
        aligned_keyframe = int(segment_time // keyframe_interval_seconds) * keyframe_interval_seconds

        output: Dict[str, Dict[str, object]] = {}
        for idx, rendition in enumerate(self.renditions):
            node = live_nodes[idx % len(live_nodes)]
            output[rendition] = {
                "url": f"{stream_id}_{rendition}_seg_{segment_id}.ts",
                "node": node,
                "keyframe_ts": aligned_keyframe,
            }
        return output


class LiveManifestManager:
    """v1 sliding window plus full history for VOD archival (improvement #3)."""

    def __init__(self, window_size: int = 5):
        self.window_size = window_size
        self.manifests: Dict[str, collections.deque] = {}
        self._history: Dict[str, List[Dict[str, str]]] = {}
        self.lock = threading.Lock()

    def append_segment(self, stream_id: str, rendition: str, segment_url: str):
        with self.lock:
            if stream_id not in self.manifests:
                self.manifests[stream_id] = collections.deque(maxlen=self.window_size)
                self._history[stream_id] = []

            entry = {"rendition": rendition, "url": segment_url}
            self.manifests[stream_id].append(entry)
            self._history[stream_id].append(dict(entry))

    def get_manifest(self, stream_id: str) -> List[Dict[str, str]]:
        with self.lock:
            if stream_id in self.manifests:
                return list(self.manifests[stream_id])
            return []

    def archive_vod(self, stream_id: str) -> List[Dict[str, str]]:
        """Convert the stream's full history into a permanent VOD playlist.

        The sliding live window drops old segments; the VOD asset must
        contain every segment in broadcast order (FOLLOW-UPS.md #4).
        Idempotent: archiving twice returns the same playlist.
        """
        with self.lock:
            return [dict(entry) for entry in self._history.get(stream_id, [])]


class OriginShieldTree:
    """v1 tiered cache plus singleflight, LRU bounds and origin metrics
    (improvement #1)."""

    def __init__(
        self,
        max_tier_entries: Optional[int] = None,
        origin_loader: Optional[Callable[[str], Optional[str]]] = None,
    ):
        # Bounded LRU tiers; None means unbounded (v1 behavior).
        self.max_tier_entries = max_tier_entries
        self.l1_cache: "collections.OrderedDict[str, str]" = collections.OrderedDict()
        self.l2_cache: "collections.OrderedDict[str, str]" = collections.OrderedDict()
        self.origin: Dict[str, str] = {}
        self.origin_loader = origin_loader
        self.origin_reads = 0
        self.lock = threading.Lock()
        self._key_monitors: Dict[str, threading.Lock] = {}
        self._key_monitors_guard = threading.Lock()

    def write_to_origin(self, key: str, value: str):
        with self.lock:
            self.origin[key] = value

    def _tier_get(self, tier: "collections.OrderedDict[str, str]", key: str) -> Optional[str]:
        if key in tier:
            tier.move_to_end(key)
            return tier[key]
        return None

    def _tier_put(self, tier: "collections.OrderedDict[str, str]", key: str, value: str):
        tier[key] = value
        tier.move_to_end(key)
        if self.max_tier_entries is not None:
            while len(tier) > self.max_tier_entries:
                tier.popitem(last=False)

    def _key_monitor(self, key: str) -> threading.Lock:
        with self._key_monitors_guard:
            if key not in self._key_monitors:
                self._key_monitors[key] = threading.Lock()
            return self._key_monitors[key]

    def _load_from_origin(self, key: str) -> Optional[str]:
        if self.origin_loader is not None:
            return self.origin_loader(key)
        with self.lock:
            return self.origin.get(key)

    def fetch(self, key: str) -> Optional[str]:
        # Fast path: already cached.
        with self.lock:
            val = self._tier_get(self.l1_cache, key)
            if val is not None:
                return val
            val = self._tier_get(self.l2_cache, key)
            if val is not None:
                self._tier_put(self.l1_cache, key, val)
                return val

        # Singleflight: concurrent misses for the same key collapse into
        # one origin load (PITFALLS.md #2: the origin should see a handful
        # of requests, not one per viewer).
        monitor = self._key_monitor(key)
        with monitor:
            with self.lock:
                val = self._tier_get(self.l1_cache, key)
                if val is None:
                    val = self._tier_get(self.l2_cache, key)
                if val is not None:
                    self._tier_put(self.l1_cache, key, val)
                    return val
                self.origin_reads += 1

            val = self._load_from_origin(key)
            if val is None:
                return None
            with self.lock:
                self._tier_put(self.l2_cache, key, val)
                self._tier_put(self.l1_cache, key, val)
            return val
