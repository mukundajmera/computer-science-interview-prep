package v2_compression;
import java.util.ArrayList;
import java.util.List;

public class GorillaCompression {
    public static class BitWriter {
        public List<Integer> bits = new ArrayList<>();
        public void writeBit(int b) { bits.add(b & 1); }
        public void writeBits(long val, int num) {
            for (int i = num - 1; i >= 0; i--) {
                writeBit((int)((val >> i) & 1));
            }
        }
    }
    
    public static class BitReader {
        public List<Integer> bits;
        public int pos = 0;
        public BitReader(List<Integer> bits) { this.bits = bits; }
        public int readBit() {
            if (pos >= bits.size()) return 0;
            return bits.get(pos++);
        }
        public long readBits(int num) {
            long val = 0;
            for (int i = 0; i < num; i++) {
                val = (val << 1) | readBit();
            }
            return val;
        }
    }
    
    public static class Compressor {
        public BitWriter writer = new BitWriter();
        Long prevTs = null;
        Long prevDelta = null;
        public int count = 0;
        
        public void addTimestamp(long ts) {
            count++;
            if (prevTs == null) {
                writer.writeBits(ts, 64);
                prevTs = ts;
                return;
            }
            if (prevDelta == null) {
                long delta = ts - prevTs;
                writer.writeBits(delta, 32);
                prevDelta = delta;
                prevTs = ts;
                return;
            }
            long delta = ts - prevTs;
            long dod = delta - prevDelta;
            
            if (dod == 0) {
                writer.writeBit(0);
            } else if (dod >= -63 && dod <= 64) {
                writer.writeBits(0b10, 2);
                writer.writeBits(dod & 0x7F, 7);
            } else if (dod >= -255 && dod <= 256) {
                writer.writeBits(0b110, 3);
                writer.writeBits(dod & 0x1FF, 9);
            } else if (dod >= -2047 && dod <= 2048) {
                writer.writeBits(0b1110, 4);
                writer.writeBits(dod & 0xFFF, 12);
            } else {
                writer.writeBits(0b1111, 4);
                writer.writeBits(dod & 0xFFFFFFFFL, 32);
            }
            prevDelta = delta;
            prevTs = ts;
        }
    }
    
    public static class Decompressor {
        BitReader reader;
        Long prevTs = null;
        Long prevDelta = null;
        
        public Decompressor(List<Integer> bits) {
            this.reader = new BitReader(bits);
        }
        
        public List<Long> readTimestamps(int count) {
            List<Long> res = new ArrayList<>();
            if (count == 0) return res;
            
            prevTs = reader.readBits(64);
            res.add(prevTs);
            if (count == 1) return res;
            
            long delta = reader.readBits(32);
            long ts = prevTs + (int)delta;
            res.add(ts);
            prevTs = ts;
            prevDelta = (long)(int)delta;
            
            for (int i = 2; i < count; i++) {
                int b1 = reader.readBit();
                long dod = 0;
                if (b1 != 0) {
                    int b2 = reader.readBit();
                    if (b2 == 0) {
                        long val = reader.readBits(7);
                        dod = val < 64 ? val : val - 128;
                    } else {
                        int b3 = reader.readBit();
                        if (b3 == 0) {
                            long val = reader.readBits(9);
                            dod = val < 256 ? val : val - 512;
                        } else {
                            int b4 = reader.readBit();
                            if (b4 == 0) {
                                long val = reader.readBits(12);
                                dod = val < 2048 ? val : val - 4096;
                            } else {
                                long val = reader.readBits(32);
                                dod = (int)val;
                            }
                        }
                    }
                }
                long curDelta = prevDelta + dod;
                long curTs = prevTs + curDelta;
                res.add(curTs);
                prevDelta = curDelta;
                prevTs = curTs;
            }
            return res;
        }
    }
}
