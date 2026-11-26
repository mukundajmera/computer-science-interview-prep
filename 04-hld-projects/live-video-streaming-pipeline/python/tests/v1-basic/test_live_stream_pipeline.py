import pytest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'v1-basic')))

from live_stream_pipeline import (
    LiveStreamIngestServer,
    AbrTranscoderLadder,
    LiveManifestManager,
    OriginShieldTree
)

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

