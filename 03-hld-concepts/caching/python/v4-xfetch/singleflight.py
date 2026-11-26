import threading
from typing import Callable, Any, Dict, TypeVar, Tuple

T = TypeVar('T')

class Call:
    def __init__(self):
        self.val = None
        self.err = None
        self.event = threading.Event()

class Singleflight:
    """
    Singleflight deduplicates concurrent function calls for the same key,
    ensuring the function is executed only once and all callers receive the
    same result.
    """
    def __init__(self):
        self._mu = threading.Lock()
        self._m: Dict[Any, Call] = {}

    def do(self, key: Any, fn: Callable[[], T]) -> Tuple[T, Exception, bool]:
        """
        Execute and return the results of the given function, making sure that
        only one execution is in-flight for a given key at a time.
        If a duplicate comes in, the duplicate caller waits for the original
        to complete and receives the same results.
        
        Returns:
            val: Result of the function
            err: Exception if raised by the function
            shared: True if the result was shared with other callers
        """
        self._mu.acquire()
        if key in self._m:
            c = self._m[key]
            self._mu.release()
            c.event.wait()
            return c.val, c.err, True

        c = Call()
        self._m[key] = c
        self._mu.release()

        try:
            c.val = fn()
        except Exception as e:
            c.err = e
        finally:
            c.event.set()
            
            self._mu.acquire()
            if key in self._m and self._m[key] is c:
                del self._m[key]
            self._mu.release()

        return c.val, c.err, False
