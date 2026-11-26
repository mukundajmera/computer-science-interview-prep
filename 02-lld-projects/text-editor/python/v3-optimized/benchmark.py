import time
from gap_buffer import GapBuffer

def benchmark():
    gb = GapBuffer(10)
    
    start_time = time.time()
    
    # Insert 100,000 lines
    for i in range(100000):
        gb.insert(i, f"Line {i}")
        
    insert_time = time.time() - start_time
    print(f"Time to insert 100,000 lines: {insert_time:.4f} seconds")
    
    # Local cursor insertions (near the end, to show O(1) performance)
    start_time = time.time()
    for i in range(1000):
        gb.insert(99000 + i, f"New Line {i}")
        
    local_insert_time = time.time() - start_time
    print(f"Time for 1,000 local cursor insertions: {local_insert_time:.4f} seconds")

if __name__ == "__main__":
    benchmark()
