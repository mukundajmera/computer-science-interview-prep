import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

import pytest
from protocol_multiplexer import ProtocolMultiplexer, Frame

def test_tcp_in_order():
    mux = ProtocolMultiplexer('TCP')
    f1 = Frame(1, 'DATA', 0, 'payload1', 0)
    f2 = Frame(2, 'DATA', 0, 'payload2', 1)
    
    mux.receive_frame(f1)
    mux.receive_frame(f2)
    
    processed = mux.get_processed_frames()
    assert len(processed) == 2
    assert processed[0] == f1
    assert processed[1] == f2
    assert len(mux.get_blocked_streams()) == 0

def test_tcp_hol_blocking():
    mux = ProtocolMultiplexer('TCP')
    f1 = Frame(1, 'DATA', 0, 'payload1', 0)
    # Frame with sequence_num 1 is "dropped"
    f3 = Frame(2, 'DATA', 0, 'payload3', 2) # Stream 2
    
    mux.receive_frame(f1)
    mux.receive_frame(f3)
    
    processed = mux.get_processed_frames()
    assert len(processed) == 1
    assert processed[0] == f1
    
    # Stream 2 is blocked because TCP expects sequence_num 1 first
    assert 2 in mux.get_blocked_streams()
    
    # Retransmit dropped frame
    f2 = Frame(1, 'DATA', 0, 'payload2', 1) # Stream 1
    mux.receive_frame(f2)
    
    processed = mux.get_processed_frames()
    assert len(processed) == 3
    assert processed[1] == f2
    assert processed[2] == f3
    assert len(mux.get_blocked_streams()) == 0

def test_quic_independent_streams():
    mux = ProtocolMultiplexer('QUIC')
    f1 = Frame(1, 'DATA', 0, 's1p1', 0)
    # Stream 1 missing sequence 1
    f3 = Frame(2, 'DATA', 0, 's2p1', 0) # Stream 2 starts at sequence 0 for its stream
    f4 = Frame(2, 'DATA', 0, 's2p2', 1)
    
    mux.receive_frame(f1)
    mux.receive_frame(f3)
    mux.receive_frame(f4)
    
    processed = mux.get_processed_frames()
    assert len(processed) == 3
    assert processed[0] == f1
    assert processed[1] == f3
    assert processed[2] == f4
    
    # Send an out of order packet for Stream 1
    f5 = Frame(1, 'DATA', 0, 's1p3', 2)
    mux.receive_frame(f5)
    
    assert len(mux.get_processed_frames()) == 3
    
    # Stream 1 is blocked waiting for sequence 1, Stream 2 is not blocked
    blocked = mux.get_blocked_streams()
    assert 1 in blocked
    assert 2 not in blocked
    
    # Retransmit sequence 1 for Stream 1
    f2 = Frame(1, 'DATA', 0, 's1p2', 1)
    mux.receive_frame(f2)
    
    assert len(mux.get_processed_frames()) == 5
    assert len(mux.get_blocked_streams()) == 0

def test_invalid_mode():
    with pytest.raises(ValueError):
        ProtocolMultiplexer('UDP')
