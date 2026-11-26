from dataclasses import dataclass
from typing import Dict, List, Set

@dataclass
class Frame:
    stream_id: int
    frame_type: str  # e.g., 'HEADERS', 'DATA'
    flags: int
    payload: str
    sequence_num: int

class ProtocolMultiplexer:
    def __init__(self, mode: str):
        """
        mode: 'TCP' or 'QUIC'
        """
        self.mode = mode.upper()
        if self.mode not in ['TCP', 'QUIC']:
            raise ValueError("Mode must be 'TCP' or 'QUIC'")
        
        self.tcp_buffer: Dict[int, Frame] = {}
        self.tcp_expected_seq = 0
        
        # For QUIC, we track sequences per stream
        self.quic_buffers: Dict[int, Dict[int, Frame]] = {}
        self.quic_expected_seqs: Dict[int, int] = {}
        
        # List to store processed frames
        self.processed_frames: List[Frame] = []

    def receive_frame(self, frame: Frame):
        if self.mode == 'TCP':
            self._handle_tcp(frame)
        else:
            self._handle_quic(frame)

    def _handle_tcp(self, frame: Frame):
        if frame.sequence_num == self.tcp_expected_seq:
            self.processed_frames.append(frame)
            self.tcp_expected_seq += 1
            # Check buffer for next frames
            while self.tcp_expected_seq in self.tcp_buffer:
                next_frame = self.tcp_buffer.pop(self.tcp_expected_seq)
                self.processed_frames.append(next_frame)
                self.tcp_expected_seq += 1
        elif frame.sequence_num > self.tcp_expected_seq:
            self.tcp_buffer[frame.sequence_num] = frame

    def _handle_quic(self, frame: Frame):
        stream_id = frame.stream_id
        if stream_id not in self.quic_expected_seqs:
            self.quic_expected_seqs[stream_id] = 0
            self.quic_buffers[stream_id] = {}
            
        expected_seq = self.quic_expected_seqs[stream_id]
        
        if frame.sequence_num == expected_seq:
            self.processed_frames.append(frame)
            self.quic_expected_seqs[stream_id] += 1
            expected_seq += 1
            
            while expected_seq in self.quic_buffers[stream_id]:
                next_frame = self.quic_buffers[stream_id].pop(expected_seq)
                self.processed_frames.append(next_frame)
                self.quic_expected_seqs[stream_id] += 1
                expected_seq += 1
        elif frame.sequence_num > expected_seq:
            self.quic_buffers[stream_id][frame.sequence_num] = frame

    def get_processed_frames(self) -> List[Frame]:
        return self.processed_frames
        
    def get_blocked_streams(self) -> Set[int]:
        """
        Returns a set of stream IDs that are currently blocked.
        In TCP, if the global expected sequence is not received but higher sequences are buffered,
        all streams associated with buffered frames are technically blocked by the missing lower sequence.
        In QUIC, only the stream with a missing sequence is blocked.
        """
        blocked = set()
        if self.mode == 'TCP':
            if self.tcp_buffer:
                # Any stream with a buffered frame is blocked by the missing global sequence
                for frame in self.tcp_buffer.values():
                    blocked.add(frame.stream_id)
        else:
            for stream_id, buffer in self.quic_buffers.items():
                if buffer:
                    blocked.add(stream_id)
        return blocked
