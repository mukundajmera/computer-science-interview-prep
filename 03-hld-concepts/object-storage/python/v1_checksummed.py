import hashlib
import time

class V1ChecksummedStore:
    """
    A basic object store that calculates MD5 checksums on upload
    and verifies them on read to detect bit rot.
    """
    def __init__(self):
        # Metadata index: key -> { 'data': bytes, 'md5': str, 'timestamp': float }
        self.metadata_index = {}

    def _calculate_md5(self, data: bytes) -> str:
        md5 = hashlib.md5()
        md5.update(data)
        return md5.hexdigest()

    def put(self, key: str, data: bytes):
        checksum = self._calculate_md5(data)
        self.metadata_index[key] = {
            'data': data,
            'md5': checksum,
            'timestamp': time.time()
        }
        return checksum

    def get(self, key: str) -> bytes:
        if key not in self.metadata_index:
            raise KeyError(f"Object {key} not found")
        
        record = self.metadata_index[key]
        current_checksum = self._calculate_md5(record['data'])
        
        if current_checksum != record['md5']:
            raise ValueError(f"Bit rot detected for {key}! Checksum mismatch.")
            
        return record['data']

    def delete(self, key: str):
        if key in self.metadata_index:
            del self.metadata_index[key]

    def corrupt_data_for_testing(self, key: str):
        """Simulates silent bit rot on the storage media"""
        if key in self.metadata_index:
            # Flip a byte
            corrupted = bytearray(self.metadata_index[key]['data'])
            if corrupted:
                corrupted[0] = corrupted[0] ^ 0xFF
            self.metadata_index[key]['data'] = bytes(corrupted)

