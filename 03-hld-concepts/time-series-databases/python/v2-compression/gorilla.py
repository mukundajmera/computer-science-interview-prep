class BitWriter:
    def __init__(self):
        self.bits = []
    def write_bit(self, bit: int):
        self.bits.append(bit & 1)
    def write_bits(self, value: int, num_bits: int):
        for i in range(num_bits - 1, -1, -1):
            self.write_bit((value >> i) & 1)

class BitReader:
    def __init__(self, bits):
        self.bits = bits
        self.pos = 0
    def read_bit(self):
        if self.pos >= len(self.bits): return 0
        b = self.bits[self.pos]
        self.pos += 1
        return b
    def read_bits(self, num_bits: int):
        val = 0
        for _ in range(num_bits):
            val = (val << 1) | self.read_bit()
        return val

class GorillaCompressor:
    def __init__(self):
        self.writer = BitWriter()
        self.prev_ts = None
        self.prev_delta = None
        self.count = 0
        
    def add_timestamp(self, ts: int):
        self.count += 1
        if self.prev_ts is None:
            self.writer.write_bits(ts, 64)
            self.prev_ts = ts
            return
            
        if self.prev_delta is None:
            delta = ts - self.prev_ts
            self.writer.write_bits(delta, 32)
            self.prev_delta = delta
            self.prev_ts = ts
            return
            
        delta = ts - self.prev_ts
        dod = delta - self.prev_delta
        
        if dod == 0:
            self.writer.write_bit(0)
        elif -63 <= dod <= 64:
            self.writer.write_bits(0b10, 2)
            self.writer.write_bits(dod & 0x7F, 7)
        elif -255 <= dod <= 256:
            self.writer.write_bits(0b110, 3)
            self.writer.write_bits(dod & 0x1FF, 9)
        elif -2047 <= dod <= 2048:
            self.writer.write_bits(0b1110, 4)
            self.writer.write_bits(dod & 0xFFF, 12)
        else:
            self.writer.write_bits(0b1111, 4)
            self.writer.write_bits(dod & 0xFFFFFFFF, 32)
            
        self.prev_delta = delta
        self.prev_ts = ts

class GorillaDecompressor:
    def __init__(self, bits):
        self.reader = BitReader(bits)
        self.prev_ts = None
        self.prev_delta = None
        
    def read_timestamp(self, count):
        res = []
        if count == 0: return res
        
        self.prev_ts = self.reader.read_bits(64)
        res.append(self.prev_ts)
        if count == 1: return res
        
        self.prev_delta = self.reader.read_bits(32)
        ts = self.prev_ts + self.prev_delta
        res.append(ts)
        self.prev_ts = ts
        
        for _ in range(2, count):
            bit = self.reader.read_bit()
            if bit == 0:
                dod = 0
            else:
                bit2 = self.reader.read_bit()
                if bit2 == 0:
                    dod_val = self.reader.read_bits(7)
                    dod = dod_val if dod_val < 64 else dod_val - 128
                else:
                    bit3 = self.reader.read_bit()
                    if bit3 == 0:
                        dod_val = self.reader.read_bits(9)
                        dod = dod_val if dod_val < 256 else dod_val - 512
                    else:
                        bit4 = self.reader.read_bit()
                        if bit4 == 0:
                            dod_val = self.reader.read_bits(12)
                            dod = dod_val if dod_val < 2048 else dod_val - 4096
                        else:
                            dod_val = self.reader.read_bits(32)
                            dod = dod_val if dod_val < (1<<31) else dod_val - (1<<32)
            
            delta = self.prev_delta + dod
            ts = self.prev_ts + delta
            res.append(ts)
            
            self.prev_delta = delta
            self.prev_ts = ts
            
        return res

class CompressedSeries:
    def __init__(self):
        self.compressor = GorillaCompressor()
        
    def add(self, ts: int):
        self.compressor.add_timestamp(ts)
        
    def range_query(self, start: int, end: int):
        d = GorillaDecompressor(self.compressor.writer.bits)
        timestamps = d.read_timestamp(self.compressor.count)
        return [t for t in timestamps if start <= t <= end]
