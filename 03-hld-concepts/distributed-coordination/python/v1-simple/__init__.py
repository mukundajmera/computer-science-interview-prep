import os
import sys

# Insert the parent directory into the sys.path to allow dynamic imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'v1-simple')))

from distributed_lock import LockServer, DistributedLock
