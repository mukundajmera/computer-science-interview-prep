import pytest
import sys
import os
import uuid
from typing import Dict, Optional

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'v1-basic')))
from video_service import (
    VideoService, InitUploadCommand, UploadSession, Video, Manifest, UploadStatus
)


class InMemoryVideoService(VideoService):
    def __init__(self):
        self.sessions: Dict[str, UploadSession] = {}
        self.videos: Dict[str, Video] = {}
        self.manifests: Dict[str, Manifest] = {}

    def init_upload(self, command: InitUploadCommand) -> UploadSession:
        session_id = str(uuid.uuid4())
        video_id = str(uuid.uuid4())
        session = UploadSession(
            session_id=session_id,
            video_id=video_id,
            status=UploadStatus.INITIATED,
            expected_parts=command.expected_parts,
            uploaded_parts=0
        )
        self.sessions[session_id] = session
        self.videos[video_id] = Video(video_id=video_id, owner_id=command.owner_id, status=UploadStatus.INITIATED)
        return session

    def upload_part(self, session_id: str, part_number: int, etag: str) -> UploadSession:
        if session_id not in self.sessions:
            raise ValueError("Session not found")
        
        session = self.sessions[session_id]
        updated_session = UploadSession(
            session_id=session.session_id,
            video_id=session.video_id,
            status=UploadStatus.PARTIAL,
            expected_parts=session.expected_parts,
            uploaded_parts=session.uploaded_parts + 1
        )
        self.sessions[session_id] = updated_session
        return updated_session

    def complete_upload(self, session_id: str, idempotency_key: str) -> Video:
        if session_id not in self.sessions:
            raise ValueError("Session not found")
        
        session = self.sessions[session_id]
        video = self.videos[session.video_id]
        
        updated_video = Video(
            video_id=video.video_id,
            owner_id=video.owner_id,
            status=UploadStatus.READY
        )
        self.videos[session.video_id] = updated_video
        
        self.manifests[session.video_id] = Manifest(
            video_id=session.video_id,
            path=f"/path/to/{session.video_id}",
            state="ready"
        )
        
        return updated_video

    def get_manifest(self, video_id: str) -> Optional[Manifest]:
        return self.manifests.get(video_id)


def test_init_upload():
    service = InMemoryVideoService()
    cmd = InitUploadCommand(owner_id="user-1", title="My Video", total_bytes=10000, expected_parts=5)
    
    session = service.init_upload(cmd)
    
    assert session.status == UploadStatus.INITIATED
    assert session.expected_parts == 5
    assert session.uploaded_parts == 0
    assert session.session_id is not None
    assert session.video_id is not None


def test_upload_part():
    service = InMemoryVideoService()
    cmd = InitUploadCommand(owner_id="user-1", title="My Video", total_bytes=10000, expected_parts=5)
    initial_session = service.init_upload(cmd)
    
    session = service.upload_part(initial_session.session_id, 1, "etag-1")
    
    assert session.status == UploadStatus.PARTIAL
    assert session.uploaded_parts == 1
    assert session.session_id == initial_session.session_id


def test_complete_upload():
    service = InMemoryVideoService()
    cmd = InitUploadCommand(owner_id="user-1", title="My Video", total_bytes=10000, expected_parts=5)
    initial_session = service.init_upload(cmd)
    service.upload_part(initial_session.session_id, 1, "etag-1")
    
    video = service.complete_upload(initial_session.session_id, "key-123")
    
    assert video.status == UploadStatus.READY
    assert video.video_id == initial_session.video_id
    assert video.owner_id == "user-1"
    
    manifest = service.get_manifest(video.video_id)
    assert manifest is not None
    assert manifest.state == "ready"
