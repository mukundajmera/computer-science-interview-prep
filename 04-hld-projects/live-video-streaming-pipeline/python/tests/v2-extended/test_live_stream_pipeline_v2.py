import pytest
import sys
import os
import threading
import time

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'v2-extended')))

from live_stream_pipeline_v2 import (
    LiveStreamIngestServer,
    AbrTranscoderLadder,
    LiveManifestManager,
    OriginShieldTree
)

# ---------------------------------------------------------------------------
# v1 parity tests: same scenarios as tests/v1-basic, run against v2.
# ---------------------------------------------------------------------------

def test_ingest_server_start_end_session():
    server = LiveStreamIngestServer()
    assert server.start_session("stream_1") == True
    assert server.is_active("stream_1") == True
    assert server.start_session("stream_1") == False
    assert server.end_session("stream_1") == True
    assert server.is_active("stream_1") == False
    assert server.end_session("stream_1") == False

def test_abr_transcoder_ladder():
    ladder = AbrTranscoderLadder()
    renditions = ladder.transcode_segment("stream_1", 42)
    assert len(renditions) == 4
    assert "1080p" in renditions
    assert renditions["720p"] == "stream_1_720p_seg_42.ts"

def test_live_manifest_manager_window():
    manager = LiveManifestManager(window_size=3)
    manager.append_segment("stream_1", "1080p", "url_1")
    manager.append_segment("stream_1", "1080p", "url_2")
    manager.append_segment("stream_1", "1080p", "url_3")
    manager.append_segment("stream_1", "1080p", "url_4")

    manifest = manager.get_manifest("stream_1")
    assert len(manifest) == 3
    assert manifest[0]["url"] == "url_2"
    assert manifest[2]["url"] == "url_4"

def test_origin_shield_tree_caching():
    shield = OriginShieldTree()
    shield.write_to_origin("seg_1", "video_data_1")

    # Fetch from origin, promotes to L1 and L2
    assert shield.fetch("seg_1") == "video_data_1"
    assert "seg_1" in shield.l1_cache
    assert "seg_1" in shield.l2_cache

    # Fetch missing
    assert shield.fetch("seg_2") is None

def test_pipeline_integration():
    ingest = LiveStreamIngestServer()
    transcoder = AbrTranscoderLadder()
    manifest_manager = LiveManifestManager()
    shield = OriginShieldTree()

    stream_id = "live_1"
    assert ingest.start_session(stream_id) == True

    segment_id = 1
    renditions = transcoder.transcode_segment(stream_id, segment_id)

    for rendition, url in renditions.items():
        shield.write_to_origin(url, f"data_for_{url}")
        manifest_manager.append_segment(stream_id, rendition, url)

    manifest = manifest_manager.get_manifest(stream_id)
    assert len(manifest) == 4

    # viewer fetches segment
    url_to_fetch = manifest[0]["url"]
    data = shield.fetch(url_to_fetch)
    assert data == f"data_for_{url_to_fetch}"

# ---------------------------------------------------------------------------
# v2-only tests: one or more per improvement.
# ---------------------------------------------------------------------------

# Improvement #1: singleflight, LRU bounds, origin metrics (FOLLOW-UPS #2,
# PITFALLS #2).

def test_singleflight_collapses_concurrent_misses():
    load_calls = []
    load_lock = threading.Lock()

    def slow_loader(key):
        with load_lock:
            load_calls.append(key)
        time.sleep(0.2)  # slow origin: exposes uncollapsed duplicate loads
        return "data_" + key

    shield = OriginShieldTree(origin_loader=slow_loader)
    barrier = threading.Barrier(8)
    results = []

    def viewer():
        barrier.wait()
        results.append(shield.fetch("seg_hot"))

    threads = [threading.Thread(target=viewer) for _ in range(8)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert results == ["data_seg_hot"] * 8
    assert load_calls == ["seg_hot"], "8 concurrent viewers must cause exactly one origin load"
    assert shield.origin_reads == 1

def test_lru_eviction_bounds_tiers():
    shield = OriginShieldTree(max_tier_entries=2)
    for i in range(3):
        shield.write_to_origin(f"seg_{i}", f"data_{i}")
        shield.fetch(f"seg_{i}")

    # L1 holds only the 2 most recently used segments.
    assert len(shield.l1_cache) == 2
    assert "seg_0" not in shield.l1_cache
    assert "seg_1" in shield.l1_cache and "seg_2" in shield.l1_cache
    # L2 is bounded too.
    assert len(shield.l2_cache) == 2
    # Evicted data is still served from the origin.
    assert shield.fetch("seg_0") == "data_0"

def test_origin_reads_metric_counts_only_tier_misses():
    shield = OriginShieldTree()
    shield.write_to_origin("a", "1")
    shield.write_to_origin("b", "2")

    shield.fetch("a")  # origin read
    shield.fetch("a")  # L1 hit
    shield.fetch("b")  # origin read
    shield.fetch("b")  # L1 hit

    assert shield.origin_reads == 2

# Improvement #2: node failover and aligned keyframes (FOLLOW-UPS #1,
# PITFALLS #4).

def test_transcoder_failover_skips_dead_node():
    ladder = AbrTranscoderLadder(nodes=["gpu-1", "gpu-2"])
    ladder.fail_node("gpu-1")

    out = ladder.transcode_segment_resilient("s1", 7)
    used_nodes = {entry["node"] for entry in out.values()}
    assert used_nodes == {"gpu-2"}, "all renditions must move to the live node"
    assert len(out) == 4

def test_transcoder_all_nodes_dead_raises():
    ladder = AbrTranscoderLadder(nodes=["gpu-1", "gpu-2"])
    ladder.fail_node("gpu-1")
    ladder.fail_node("gpu-2")

    with pytest.raises(RuntimeError):
        ladder.transcode_segment_resilient("s1", 7)

def test_transcoder_revive_restores_node():
    ladder = AbrTranscoderLadder(nodes=["gpu-1"])
    ladder.fail_node("gpu-1")
    ladder.revive_node("gpu-1")
    out = ladder.transcode_segment_resilient("s1", 1)
    assert {e["node"] for e in out.values()} == {"gpu-1"}

def test_keyframes_aligned_across_renditions():
    ladder = AbrTranscoderLadder(nodes=["gpu-1", "gpu-2"])
    out = ladder.transcode_segment_resilient("s1", 5, keyframe_interval_seconds=2.0)

    keyframes = {entry["keyframe_ts"] for entry in out.values()}
    assert len(keyframes) == 1, "every rendition of a segment shares one IDR boundary"
    # segment_time = 5 * 2.0 = 10.0, aligned down to the 2s interval = 10.0
    assert keyframes.pop() == 10.0

# Improvement #3: live-to-VOD archival (FOLLOW-UPS #4).

def test_archive_vod_keeps_full_history_beyond_window():
    manager = LiveManifestManager(window_size=3)
    for i in range(6):
        manager.append_segment("s1", "1080p", f"url_{i}")

    live = manager.get_manifest("s1")
    assert len(live) == 3, "live window still slides"
    assert live[0]["url"] == "url_3"

    vod = manager.archive_vod("s1")
    assert len(vod) == 6, "VOD asset keeps every segment"
    assert [e["url"] for e in vod] == [f"url_{i}" for i in range(6)]

def test_archive_vod_idempotent_and_unknown_stream():
    manager = LiveManifestManager()
    manager.append_segment("s1", "720p", "url_0")

    first = manager.archive_vod("s1")
    second = manager.archive_vod("s1")
    assert first == second
    assert manager.archive_vod("never_streamed") == []
