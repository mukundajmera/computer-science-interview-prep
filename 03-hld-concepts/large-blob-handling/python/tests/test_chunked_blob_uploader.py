import pytest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'v1-simple')))

from chunked_blob_uploader import ChunkedBlobUploader

@pytest.fixture
def uploader():
    return ChunkedBlobUploader()

def test_successful_upload_and_retrieval(uploader):
    chunk1 = b"Hello, "
    chunk2 = b"World!"
    full_data = b"Hello, World!"
    expected_sha256 = ChunkedBlobUploader.compute_sha256(full_data)

    session_id = uploader.initiate_session("blob-1", 2, len(full_data), expected_sha256)
    assert session_id is not None

    uploader.upload_chunk(session_id, 0, chunk1)
    missing_chunks = uploader.get_missing_chunks(session_id)
    assert len(missing_chunks) == 1
    assert 1 in missing_chunks

    uploader.upload_chunk(session_id, 1, chunk2)
    assert len(uploader.get_missing_chunks(session_id)) == 0

    assert uploader.complete_session(session_id) is True

    retrieved = uploader.get_blob("blob-1")
    assert retrieved is not None
    assert retrieved == full_data

def test_upload_with_invalid_session(uploader):
    with pytest.raises(ValueError, match="Invalid session ID"):
        uploader.upload_chunk("invalid-session", 0, b"")

    with pytest.raises(ValueError, match="Invalid session ID"):
        uploader.get_missing_chunks("invalid-session")

    with pytest.raises(ValueError, match="Invalid session ID"):
        uploader.complete_session("invalid-session")

def test_incomplete_session_completion(uploader):
    chunk1 = b"Hello, "
    full_data = b"Hello, World!"
    expected_sha256 = ChunkedBlobUploader.compute_sha256(full_data)

    session_id = uploader.initiate_session("blob-2", 2, len(full_data), expected_sha256)

    uploader.upload_chunk(session_id, 0, chunk1)

    assert uploader.complete_session(session_id) is False
    assert uploader.get_blob("blob-2") is None

def test_checksum_mismatch(uploader):
    chunk1 = b"Hello, "
    chunk2 = b"Wrong!"
    full_data = b"Hello, World!"
    expected_sha256 = ChunkedBlobUploader.compute_sha256(full_data)

    session_id = uploader.initiate_session("blob-3", 2, len(full_data), expected_sha256)

    uploader.upload_chunk(session_id, 0, chunk1)
    uploader.upload_chunk(session_id, 1, chunk2)

    with pytest.raises(ValueError, match="Checksum mismatch"):
        uploader.complete_session(session_id)
    assert uploader.get_blob("blob-3") is None

def test_invalid_chunk_index(uploader):
    full_data = b"Test"
    expected_sha256 = ChunkedBlobUploader.compute_sha256(full_data)
    session_id = uploader.initiate_session("blob-4", 1, len(full_data), expected_sha256)

    with pytest.raises(ValueError, match="Invalid chunk index"):
        uploader.upload_chunk(session_id, -1, full_data)

    with pytest.raises(ValueError, match="Invalid chunk index"):
        uploader.upload_chunk(session_id, 1, full_data)
