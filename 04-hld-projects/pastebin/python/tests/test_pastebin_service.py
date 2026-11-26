import time
import os
import sys

# Setup sys.path as per memory requirements
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'v1-basic')))

from base62 import encode, decode
from pastebin_service import PastebinService, PasteMetadata, TokenBucket

def test_base62_encoding_integrity():
    assert encode(0) == '0'
    assert encode(1) == '1'
    assert encode(10) == 'a'
    assert encode(36) == 'A'
    assert encode(61) == 'Z'
    assert encode(62) == '10'
    
    # Bijective check
    test_nums = [0, 1, 62, 1000, 1000000000]
    for num in test_nums:
        assert decode(encode(num)) == num

def test_create_and_get_paste():
    service = PastebinService()
    content = "Hello, Pastebin!"
    ip = "127.0.0.1"
    
    short_link = service.create_paste(content, ip)
    assert short_link is not None
    assert len(short_link) >= 7
    
    retrieved = service.get_paste(short_link)
    assert retrieved == content

def test_expiration_ttl_handling():
    service = PastebinService()
    content = "Ephemeral content"
    ip = "127.0.0.2"
    
    short_link = service.create_paste(content, ip, ttl_seconds=1)
    assert short_link is not None
    
    # Immediately accessible
    assert service.get_paste(short_link) == content
    
    # Wait for expiration
    time.sleep(1.1)
    
    # Passive expiration on read
    assert service.get_paste(short_link) is None

def test_rate_limiter_exceeded():
    # Capacity 2, fill rate 0.5/sec
    service = PastebinService(capacity=2, fill_rate=0.5)
    ip = "127.0.0.3"
    
    link1 = service.create_paste("1", ip)
    link2 = service.create_paste("2", ip)
    link3 = service.create_paste("3", ip)
    
    assert link1 is not None
    assert link2 is not None
    assert link3 is None  # Should be rate limited

def test_batch_ttl_cleanup_sweep():
    service = PastebinService()
    ip = "127.0.0.4"
    
    link1 = service.create_paste("Persist", ip)
    link2 = service.create_paste("Die1", ip, ttl_seconds=1)
    link3 = service.create_paste("Die2", ip, ttl_seconds=1)
    
    assert link1 is not None
    assert link2 is not None
    assert link3 is not None
    
    # Before expiration
    assert service.sweep_expired_pastes() == 0
    
    time.sleep(1.1)
    
    # Sweeper should clean up expired pastes
    assert service.sweep_expired_pastes() == 2
    
    # Links should be gone
    assert service.get_paste(link2) is None
    assert service.get_paste(link3) is None
    # Persistent link remains
    assert service.get_paste(link1) == "Persist"
